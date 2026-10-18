import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {DetailTextures} from './detail-textures.js?v=texture1';
import {createEffects} from './effects.js';
import {improveMaterials,setupLighting} from './appearance.js';
const status=document.querySelector('#status'),button=document.querySelector('#run');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(1100,420);renderer.setPixelRatio(1);
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.85;document.body.append(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color('#171c21');
const camera=new THREE.PerspectiveCamera(55,1100/420,.025,650);
setupLighting(scene,renderer).setMode('outside');
const draco=new DRACOLoader().setDecoderPath('./vendor/draco/');
const {scene:car}=await new GLTFLoader().setDRACOLoader(draco).loadAsync('./overview/car-6.glb');
improveMaterials(car,{overview:true});scene.add(car);
const box=new THREE.Box3().setFromObject(car),center=box.getCenter(new THREE.Vector3());
camera.position.set(center.x+11,2.75,center.z+.4);camera.lookAt(center.x,2.6,center.z);
const effects=createEffects(renderer,scene,camera);effects.resize(1100,420);effects.setMode('outside');
let details,hover=false;const results=[];
function draw(){effects.setHighlight(hover?car:null);effects.render();}
const baseline=new Map();
function inspect(cycle,phase){
 const gl=renderer.getContext(),pixels=new Uint8Array(1100*420*4);gl.readPixels(0,0,1100,420,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
 let hash=2166136261;for(const value of pixels)hash=Math.imul(hash^value,16777619)>>>0;
 if(!baseline.has(phase))baseline.set(phase,hash);

 const checks=[...details.materials].map(m=>({name:m.name,current:renderer.properties.get(m).uniforms.exteriorBase===details.uniforms.exteriorBase}));
 const row={cycle,phase,pass:checks.every(c=>c.current)&&baseline.get(phase)===hash,pixelHash:hash,checks,textures:renderer.info.memory.textures,programs:renderer.info.programs.length};
 results.push(row);status.textContent=JSON.stringify(results,null,2);console.log('TEXTURE_QA '+JSON.stringify(row));return row.pass;
}
draw();button.disabled=false;status.textContent='Модель загружена. Нажмите проверку.';
button.onclick=async()=>{
 button.disabled=true;results.length=0;baseline.clear();
 try{
  for(let cycle=1;cycle<=5;cycle++){
   details?.dispose();hover=false;draw();hover=true;draw();hover=false;
   details=new DetailTextures(renderer,car,6,{exteriorOnly:true});await details.ready;
   const deadline=performance.now()+10000;
   while(!details.manifests[1]&&performance.now()<deadline)await new Promise(r=>setTimeout(r,30));
   details.update(performance.now(),camera);
   while(details.slots.some(s=>s.key&&!s.texture)&&performance.now()<deadline)await new Promise(r=>setTimeout(r,30));
   if(!details.slots.some(s=>s.texture))throw Error('HD tiles did not load');

   draw();inspect(cycle,'close');
   hover=true;draw();inspect(cycle,'hover');
   hover=false;draw();inspect(cycle,'leave');
  }
  status.dataset.result=results.every(r=>r.pass)?'PASS':'FAIL';
  status.textContent=status.dataset.result+'\n'+JSON.stringify(results,null,2);
 }catch(e){status.textContent=e.stack;status.dataset.result='ERROR';}finally{button.disabled=false;}
};
