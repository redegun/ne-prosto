import * as THREE from 'three';

// An open architectural section keeps the whole train visible from the platform.
export function createStation(length=180){
 const station=new THREE.Group();station.name='Metro station';
 const mat=(color,roughness=.8,metalness=0)=>new THREE.MeshStandardMaterial({color,roughness,metalness,envMapIntensity:.15});
 const concrete=mat('#343b40'),stone=mat('#494d4c'),wall=mat('#303a41'),trim=mat('#788084',.42,.6),black=mat('#10161b'),edge=mat('#b8a16c');
 const lamp=new THREE.MeshStandardMaterial({color:'#d3d6ca',emissive:'#fff1ce',emissiveIntensity:1.6,roughness:.5});
 const geo=new THREE.BoxGeometry(1,1,1),foreground=[];
 function box(size,pos,material){const o=new THREE.Mesh(geo,material);o.scale.set(...size);o.position.set(...pos);station.add(o);return o;}
 // Track bed, sleepers and rails; the rail top is at the original wheel contact height.
 box([4.1,.35,length],[0,-.3,0],black);
 for(let z=-length/2;z<length/2;z+=.85)box([2.5,.12,.2],[0,-.13,z],concrete);
 for(const x of [-.76,.76])box([.07,.13,length],[x,-.04,0],trim);
 // A broad platform on the camera side, a tiled wall behind the train.
 box([8,.95,length],[5.75,.53,0],concrete);
 box([8,.09,length],[5.75,1.05,0],stone);
 box([.15,.025,length-.8],[1.96,1.11,0],edge);
 box([.32,6.2,length],[-3.3,2.95,0],wall);
 box([.09,.22,length-.8],[-3.08,1.4,0],trim);
 box([.09,.08,length-.8],[-3.08,3.95,0],black);
 for(let z=-length/2+2;z<length/2;z+=3.6)box([.02,4.9,.018],[-3.12,2.9,z],black);
 for(const y of [2.05,2.9,3.75])box([.025,.018,length],[-3.12,y,0],black);
 // Slim columns, ceiling beams and light strips outline the hall without a blocking roof.
 for(let z=-length/2+5;z<length/2;z+=13){
  foreground.push(box([.48,4.9,.58],[8.4,3.55,z],stone));
  foreground.push(box([.7,.18,.8],[8.4,1.23,z],trim));
  foreground.push(box([.72,.18,.8],[8.4,5.9,z],trim));
  box([11.5,.22,.22],[2.7,6.03,z],concrete);
  box([2.3,.1,.32],[5.3,5.84,z],lamp);
  box([.06,.45,2.4],[-3.1,4.65,z],lamp);
 }
 box([.24,.3,length],[8.4,6,0],concrete);
 box([.2,.25,length],[-3.3,6,0],concrete);
 // Pools of light stay local; most fixtures use emissive surfaces without costly point lights.
 for(const z of [-57,0,57]){
  const light=new THREE.PointLight('#ffe9c5',16,24,2);light.position.set(4.5,5.2,z);station.add(light);
 }
 // Tunnel portals give the cutaway a clear metro setting at both ends.
 for(const z of [-length/2,length/2]){
  box([3.6,1.3,.6],[0,4.65,z],concrete);
  for(const x of [-2,2])box([.5,4.8,.6],[x,2.1,z],concrete);
  box([4.3,.2,6],[0,-.35,z+(z>0?3:-3)],black);
 }
 const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=160;
 const ctx=canvas.getContext('2d');ctx.fillStyle='#141c23';ctx.fillRect(0,0,1024,160);
 ctx.fillStyle='#eee8d9';ctx.font='500 64px Arial';ctx.textAlign='center';ctx.fillText('СТАНКИН',512,89);
 ctx.font='24px Arial';ctx.fillStyle='#9fa9af';ctx.fillText('НАУКА · ТЕХНОЛОГИИ · БУДУЩЕЕ',512,133);
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
 const signMat=new THREE.MeshBasicMaterial({map:texture});
 for(const z of [-52,0,52]){
  const sign=new THREE.Mesh(new THREE.PlaneGeometry(6.4,1),signMat);sign.rotation.y=Math.PI/2;sign.position.set(-3.1,3.45,z);station.add(sign);
 }
 const roof=box([13.2,.18,length],[3.2,6.25,0],concrete);
 roof.material=new THREE.MeshStandardMaterial({color:'#343b40',roughness:.9,side:THREE.DoubleSide,envMapIntensity:.15});
 // The inspection camera may back up to fit a full carriage on portrait screens.
 // Continue the platform under it and omit foreground columns in this cutaway view.
 const platformExtension=box([65,.09,length],[42.25,1.05,0],stone);
 platformExtension.visible=false;
 let closeView=null;
 station.setCloseView=enabled=>{
  if(enabled===closeView)return;closeView=enabled;
  roof.visible=enabled;platformExtension.visible=enabled;foreground.forEach(o=>{o.visible=!enabled;});
  roof.scale.x=enabled?80:13.2;roof.position.x=enabled?36.7:3.2;
 };
 roof.visible=false;
 const batches=new Map();
 for(const mesh of [...station.children]){
  if(!mesh.isMesh||mesh.geometry!==geo||mesh===roof||mesh===platformExtension||foreground.includes(mesh))continue;
  if(!batches.has(mesh.material))batches.set(mesh.material,[]);
  batches.get(mesh.material).push(mesh);
 }
 for(const [material,meshes] of batches){
  const batch=new THREE.InstancedMesh(geo,material,meshes.length);
  meshes.forEach((mesh,i)=>{mesh.updateMatrix();batch.setMatrixAt(i,mesh.matrix);station.remove(mesh);});
  batch.instanceMatrix.needsUpdate=true;batch.computeBoundingSphere();station.add(batch);
 }
 return station;
}
