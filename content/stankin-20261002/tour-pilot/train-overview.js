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
 constructor(renderer,draco){this.renderer=renderer;this.draco=draco;this.root=new THREE.Group();this.cars=[];this.dead=false;this.highlighted=0;}
 async load(progress){
  let next=1,done=0;
  const worker=async()=>{
   while(next<=8&&!this.dead){
    const number=next++;
    const gltf=await new GLTFLoader().setDRACOLoader(this.draco).loadAsync('./overview/car-'+number+'.glb?v=20261017');
    if(this.dead){disposeTree(gltf.scene);return;}
    const car=gltf.scene;improveMaterials(car,{overview:true});
    const box=new THREE.Box3().setFromObject(car),center=box.getCenter(new THREE.Vector3());
    car.position.x-=center.x;car.position.z-=center.z;car.userData.length=box.max.z-box.min.z;
    car.userData.car=number;
    car.traverse(o=>{
     o.userData.car=number;
     if(o.isMesh)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{
      if(m.map)m.map.anisotropy=Math.min(8,this.renderer.capabilities.getMaxAnisotropy());
     });
    });
    this.cars[number-1]=car;this.root.add(car);progress(++done);
   }
  };
  const work=await Promise.allSettled([worker(),worker()]);
  const failed=work.find(r=>r.status==='rejected');
  if(failed){this.dispose();throw failed.reason;}
  let end=0;
  for(const car of this.cars){const half=car.userData.length/2;car.position.z+=end-half;end-=car.userData.length;}
  for(const car of this.cars)car.position.z-=end/2;
  this.root.updateMatrixWorld(true);
  this.bounds=new THREE.Box3().setFromObject(this.root);
  this.centers=this.cars.map(car=>new THREE.Box3().setFromObject(car).getCenter(new THREE.Vector3()).z);
  // Existing coupler tips now meet; original meshes and body proportions are unchanged.

 }
 highlight(number){this.highlighted=number;}
 dispose(){if(this.dead)return;this.dead=true;disposeTree(this.root);this.root.clear();this.cars=[];}
}
