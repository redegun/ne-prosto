import * as THREE from 'three';
const SLOT_COUNT=6, UV_SPLIT=.425;
export class DetailTextures {
 constructor(renderer,root,car,{exteriorOnly=false,onChange=()=>{}}={}){
  this.onChange=onChange;this.exteriorOnly=exteriorOnly;
  this.renderer=renderer;this.root=root;this.car=car;this.dead=false;this.next=0;this.retryAfter=new Map();this.meshes=[];this.materials=new Set();this.manifests={};
  this.mobile=matchMedia('(max-width:720px)').matches;this.limit=this.mobile?4:6;
  this.slots=Array.from({length:SLOT_COUNT},()=>({key:null,texture:null,request:0}));
  this.ray=new THREE.Raycaster();this.point=new THREE.Vector2();this.loader=new THREE.TextureLoader();
  root.traverse(o=>{if(o.isMesh&&(Array.isArray(o.material)?o.material:[o.material]).some(m=>m.map&&/^vagon/i.test(m.name))){this.meshes.push(o);(Array.isArray(o.material)?o.material:[o.material]).filter(m=>m.map&&/^vagon/i.test(m.name)).forEach(m=>this.materials.add(m));}});
  this.base=[...this.materials][0]?.map;this.previous=new Map([...this.materials].map(m=>[m,{compile:m.onBeforeCompile,key:m.customProgramCacheKey}]));
  this.uniforms={exteriorBase:{value:this.base},exteriorReady:{value:false}};
  for(let i=0;i<SLOT_COUNT;i++){this.uniforms['detailMap'+i]={value:this.base};this.uniforms['detailCell'+i]={value:new THREE.Vector3(-99,-99,-1)};this.uniforms['detailRect'+i]={value:new THREE.Vector4(0,0,1,1)};}
  this.materials.forEach(material=>{
   material.onBeforeCompile=shader=>{
    Object.assign(shader.uniforms,this.uniforms);
    let declarations='uniform sampler2D exteriorBase;uniform bool exteriorReady;\n';
    let sampling='vec2 detailUv=fract(vMapUv);float detailDomain=1.0-step(0.425,detailUv.y);vec3 detailCell=vec3(floor(detailUv*8.0),detailDomain);vec4 sampledDiffuseColor=texture2D(map,vMapUv);if(detailDomain>0.5&&exteriorReady){sampledDiffuseColor=texture2D(exteriorBase,vec2(detailUv.x,detailUv.y/0.425));}';
    for(let i=0;i<SLOT_COUNT;i++){
     declarations+='uniform sampler2D detailMap'+i+';uniform vec3 detailCell'+i+';uniform vec4 detailRect'+i+';\n';
     sampling+='if(all(equal(detailCell,detailCell'+i+'))){sampledDiffuseColor=texture2D(detailMap'+i+',(detailUv-detailRect'+i+'.xy)*detailRect'+i+'.zw);}';
    }
    shader.fragmentShader=declarations+shader.fragmentShader.replace('#include <map_fragment>','#ifdef USE_MAP\n'+sampling+'\ndiffuseColor*=sampledDiffuseColor;\n#endif');
   };
   material.customProgramCacheKey=()=> 'stankin-interior-exterior-tiles-v2';
   material.needsUpdate=true;
  });
  this.ready=this.loader.loadAsync('./exterior/car-'+car+'.jpg?v=20261015').then(texture=>{
   if(this.dead){texture.dispose();return;}
   this.configure(texture);this.exterior=texture;this.uniforms.exteriorBase.value=texture;this.uniforms.exteriorReady.value=true;this.onChange();
  });
  for(const domain of (exteriorOnly?[1]:[0,1]))fetch(this.folder(domain)+'/manifest.json').then(r=>{if(!r.ok)throw Error('Details unavailable');return r.json();}).then(m=>{if(!this.dead){this.manifests[domain]=m;this.next=0;this.onChange();}}).catch(()=>{});
 }
 folder(domain){return './'+(domain?'exterior-details':'details')+'/car-'+this.car;}
 configure(texture){texture.colorSpace=THREE.SRGBColorSpace;texture.flipY=false;texture.anisotropy=Math.min(16,this.renderer.capabilities.getMaxAnisotropy());texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;}
 update(now,camera){
  if(this.dead||now<this.next)return;this.next=now+650;
  camera.updateMatrixWorld();this.root.updateMatrixWorld(true);
  const scores=new Map();
  for(const y of [-.75,-.3,.15,.6])for(const x of [-.94,-.6,-.25,.25,.6,.94]){
   this.point.set(x,y);this.ray.setFromCamera(this.point,camera);
   const hit=this.ray.intersectObjects(this.meshes,false).find(h=>h.uv&&h.distance<12);
   if(!hit)continue;
   const mat=Array.isArray(hit.object.material)?hit.object.material[hit.face.materialIndex]:hit.object.material;
   if(!mat?.map||!/^vagon/i.test(mat.name))continue;
   const uv=hit.uv.clone();mat.map.transformUv(uv);
   const col=Math.min(7,Math.floor(uv.x*8)),row=Math.min(7,Math.floor(uv.y*8)),domain=uv.y<UV_SPLIT?1:0,cell=col+'-'+row,key=domain+':'+cell;
   if(!this.manifests[domain]?.tiles[cell]||(this.retryAfter.get(key)||0)>now)continue;
   const score=(1+Math.abs(x)*.15)/Math.max(.5,hit.distance);
   scores.set(key,(scores.get(key)||0)+score);
  }
  const wanted=[...scores].sort((a,b)=>b[1]-a[1]).slice(0,this.limit).map(v=>v[0]);
  for(let i=0;i<this.limit;i++){
   const slot=this.slots[i];
   if(slot.key&&!wanted.includes(slot.key)){slot.texture?.dispose();slot.texture=null;slot.key=null;slot.request++;this.uniforms['detailCell'+i].value.set(-99,-99,-1);this.uniforms['detailMap'+i].value=this.base;this.onChange();}
  }
  for(const key of wanted){
   if(this.slots.some(s=>s.key===key))continue;
   const i=this.slots.findIndex((s,index)=>index<this.limit&&!s.key);if(i<0)break;
   const slot=this.slots[i];slot.key=key;const request=++slot.request;
   const [domainString,cell]=key.split(':'),domain=Number(domainString);
   this.loader.load(this.folder(domain)+'/'+cell+(this.mobile?'-mobile':'')+'.jpg',texture=>{
    if(this.dead||slot.key!==key||slot.request!==request){texture.dispose();return;}
    this.configure(texture);slot.texture=texture;this.uniforms['detailMap'+i].value=texture;
    this.uniforms['detailCell'+i].value.set(...cell.split('-').map(Number),domain);
    this.uniforms['detailRect'+i].value.fromArray(this.manifests[domain].tiles[cell].rect);this.onChange();
   },undefined,()=>{if(!this.dead&&slot.key===key&&slot.request===request){slot.key=null;this.retryAfter.set(key,performance.now()+30000);}});
  }
 }
 dispose(){this.dead=true;for(const [m,old] of this.previous){m.onBeforeCompile=old.compile;m.customProgramCacheKey=old.key;m.needsUpdate=true;}this.previous.clear();this.exterior?.dispose();for(const slot of this.slots)slot.texture?.dispose();this.meshes=[];this.materials.clear();}
}
