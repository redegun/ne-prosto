import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { improveMaterials } from './appearance.js?v=station2';

export function disposeTree(root){
 const geometry=new Set(),materials=new Set(),textures=new Set();
 root.traverse(o=>{if(o.geometry)geometry.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));});
 materials.forEach(m=>Object.values(m).forEach(t=>{if(t?.isTexture)textures.add(t);}));
 geometry.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>{t.dispose();t.source?.data?.close?.();});
}
export class TrainOverview{
 constructor(renderer,draco){this.renderer=renderer;this.draco=draco;this.root=new THREE.Group();this.cars=[];this.dead=false;this.highlighted=0;this.originals=new Map();}
 async load(progress){
  let next=1,done=0;
  const worker=async()=>{
   while(next<=8&&!this.dead){
    const number=next++;
    const gltf=await new GLTFLoader().setDRACOLoader(this.draco).loadAsync('./overview/car-'+number+'.glb?v=20261017');
    if(this.dead){disposeTree(gltf.scene);return;}
    const car=gltf.scene;improveMaterials(car,{overview:true});
    const box=new THREE.Box3().setFromObject(car),center=box.getCenter(new THREE.Vector3());
    car.position.x-=center.x;car.position.z-=center.z;car.position.z+=(4.5-number)*20.5;
    car.userData.car=number;
    car.traverse(o=>{
     o.userData.car=number;
     if(o.isMesh)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{
      if(m.map)m.map.anisotropy=Math.min(8,this.renderer.capabilities.getMaxAnisotropy());
      if(m.emissive&&!this.originals.has(m))this.originals.set(m,{color:m.emissive.clone(),intensity:m.emissiveIntensity});
     });
    });
    this.cars[number-1]=car;this.root.add(car);progress(++done);
   }
  };
  const work=await Promise.allSettled([worker(),worker()]);
  const failed=work.find(r=>r.status==='rejected');
  if(failed){this.dispose();throw failed.reason;}
 }
 highlight(number){
  if(this.highlighted===number)return;
  for(const n of [this.highlighted,number]){
   const car=this.cars[n-1];if(!car)continue;
   car.traverse(o=>{if(o.isMesh)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{
    const original=this.originals.get(m);if(!original)return;
    if(n===number){m.emissive.set('#9bafa9');m.emissiveIntensity=.16;}
    else{m.emissive.copy(original.color);m.emissiveIntensity=original.intensity;}
   });});
  }
  this.highlighted=number;
 }
 dispose(){if(this.dead)return;this.dead=true;disposeTree(this.root);this.root.clear();this.cars=[];this.originals.clear();}
}
