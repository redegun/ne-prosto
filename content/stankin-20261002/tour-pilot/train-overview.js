import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { improveMaterials } from './appearance.js?v=station2';

export function disposeTree(root){
 const geometry=new Set(),materials=new Set(),textures=new Set();
 root.traverse(o=>{if(o.geometry)geometry.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));});
 materials.forEach(m=>Object.values(m).forEach(t=>{if(t?.isTexture)textures.add(t);}));
 geometry.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>{t.dispose();t.source?.data?.close?.();});
}

// Batch only exactly equivalent materials; branding keeps its own UV/material.
function batchCar(car){
 const count=()=>{let meshes=0,triangles=0;car.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;}});return {meshes,triangles};};
 const before=count();
 car.updateMatrixWorld(true);
 const inverse=car.matrixWorld.clone().invert(),groups=new Map(),meta={textures:{},images:{}};
 car.traverse(mesh=>{
  if(!mesh.isMesh||mesh.isSkinnedMesh||Array.isArray(mesh.material)||/^vagon/i.test(mesh.material.name))return;
  const data=mesh.material.toJSON(meta);delete data.uuid;delete data.name;
  const attributes=Object.entries(mesh.geometry.attributes).map(([k,a])=>[k,a.itemSize,a.normalized,a.array.constructor.name]);
  const key=JSON.stringify([data,attributes,!!mesh.geometry.index,mesh.castShadow,mesh.receiveShadow]);
  if(!groups.has(key))groups.set(key,[]);groups.get(key).push(mesh);
 });
 const removed=new Set(),originalGeometry=new Set();
 for(const meshes of groups.values()){
  if(meshes.length<2)continue;
  const parts=meshes.map(mesh=>mesh.geometry.clone().applyMatrix4(inverse.clone().multiply(mesh.matrixWorld)));
  const geometry=mergeGeometries(parts,false);parts.forEach(g=>g.dispose());
  if(!geometry)continue;
  geometry.computeBoundingBox();geometry.computeBoundingSphere();
  const merged=new THREE.Mesh(geometry,meshes[0].material);
  merged.castShadow=meshes[0].castShadow;merged.receiveShadow=meshes[0].receiveShadow;
  merged.name='Batched '+meshes[0].material.name;car.add(merged);
  meshes.forEach(mesh=>{originalGeometry.add(mesh.geometry);removed.add(mesh.material);mesh.removeFromParent();});
 }
 const keptMaterials=new Set(),keptGeometry=new Set();
 car.traverse(mesh=>{if(mesh.isMesh){keptGeometry.add(mesh.geometry);(Array.isArray(mesh.material)?mesh.material:[mesh.material]).forEach(m=>keptMaterials.add(m));}});
 originalGeometry.forEach(g=>{if(!keptGeometry.has(g))g.dispose();});
 removed.forEach(m=>{if(!keptMaterials.has(m))m.dispose();});
 car.userData.batchStats={before,after:count()};
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
    batchCar(car);
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
  this.centers=this.cars.map(car=>{
   const box=new THREE.Box3().setFromObject(car);car.userData.pickBox=box.clone();car.userData.pickBox.min.y=Math.max(1.095,box.min.y);
   return box.getCenter(new THREE.Vector3()).z;
  });
  this.root.traverse(o=>{o.updateMatrix();o.matrixAutoUpdate=false;});
  if(new URLSearchParams(location.search).has('profile'))console.log('TOUR_BATCHES '+JSON.stringify(this.cars.map(car=>({car:car.userData.car,...car.userData.batchStats}))));
  // Existing coupler tips now meet; original meshes and body proportions are unchanged.

 }
 hitBounds(ray){
  let nearest=null,distance=Infinity;const point=new THREE.Vector3();
  for(const car of this.cars){
   const box=car.userData.pickBox;if(!box||!ray.intersectBox(box,point))continue;
   const d=point.distanceToSquared(ray.origin);
   if(d<distance){distance=d;nearest={car:car.userData.car,point:point.clone()};}
  }
  return nearest;
 }
 highlight(number){this.highlighted=number;}
 dispose(){if(this.dead)return;this.dead=true;disposeTree(this.root);this.root.clear();this.cars=[];}
}
