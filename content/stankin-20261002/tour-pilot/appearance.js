import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export function setupLighting(scene,renderer){
 const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();
 const environment=pmrem.fromScene(room,.035);scene.environment=environment.texture;scene.environmentIntensity=.5;room.dispose();pmrem.dispose();
 scene.background=new THREE.Color('#e7e4de');
 scene.add(new THREE.HemisphereLight(0xffffff,0xb1aca3,.45));
 const lights=[];
 for(const z of [-7,-3.5,0,3.5,7]){
  const lamp=new THREE.SpotLight(0xfff8ed,3.2,9,1.35,.85,2);lamp.position.set(0,3.04,z);lamp.target.position.set(0,1,z);scene.add(lamp,lamp.target);lights.push(lamp);
 }
 const fill=new THREE.DirectionalLight(0xffffff,.35);fill.position.set(1,5,2);scene.add(fill);
 // A neutral display hall supplies visible depth through the windows.
 const hall=new THREE.Group(),wallMat=new THREE.MeshStandardMaterial({color:0xd8d5ce,roughness:.85});
 for(const side of [-1,1]){
  const wall=new THREE.Mesh(new THREE.BoxGeometry(.15,6,50),wallMat);wall.position.set(side*7,2,0);hall.add(wall);
  for(let z=-20;z<=20;z+=2.5){
   const pillar=new THREE.Mesh(new THREE.BoxGeometry(.28,5,.4),new THREE.MeshStandardMaterial({color:0xa9aaa6,roughness:.65}));
   pillar.position.set(side*4.8,2,z);hall.add(pillar);
  }
  const rail=new THREE.Mesh(new THREE.BoxGeometry(.08,.14,48),new THREE.MeshStandardMaterial({color:0x999b98,metalness:.35,roughness:.45}));
  rail.position.set(side*6.8,2.55,0);hall.add(rail);
 }
 scene.add(hall);
 return {environment,lights,hall};
}
export function improveMaterials(root){
 const replacements=new Map();
 root.traverse(object=>{
  if(!object.isMesh)return;
  const originals=Array.isArray(object.material)?object.material:[object.material];
  const result=originals.map(mat=>{
   if(replacements.has(mat))return replacements.get(mat);
   const name=mat.name.toLowerCase();let next=mat;
   if(name.includes('glass')){
    next=new THREE.MeshPhysicalMaterial({name:mat.name,color:0xffffff,roughness:.025,metalness:0,transmission:.98,thickness:.008,ior:1.46,envMapIntensity:.55,side:THREE.FrontSide});
    next.depthWrite=false;
   }else if(name.startsWith('fabric')){
    mat.color.set('#767771');mat.metalness=0;mat.roughness=.88;
   }else if(name.startsWith('seatcushion')){
    mat.color.setRGB(.0137,.0242,.0999);mat.metalness=0;mat.roughness=.83;
   }else if(name.startsWith('seatplastic')){
    mat.color.set('#dedbd2');mat.metalness=0;mat.roughness=.38;
   }else if(/silver|steel|holdbar/.test(name)){
    mat.color.set('#b7b9b8');mat.metalness=.9;mat.roughness=.28;mat.envMapIntensity=1.15;
   }else if(name.startsWith('black matte')){
    mat.color.set('#242522');mat.roughness=.65;mat.metalness=.5;
   }else if(name.startsWith('vagon')){
    mat.color.set('#ffffff');mat.metalness=0;mat.roughness=.68;mat.envMapIntensity=.4;
   }
   if(next!==mat)mat.dispose();
   replacements.set(mat,next);return next;
  });
  object.material=Array.isArray(object.material)?result:result[0];
 });
}
