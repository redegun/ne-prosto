import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const CEILING_LAMPS=new Set(['Material.013','Material.044','Material.005','Material.070','Material.075','Material.080','Material.085','Material.090','Material.063','Material.058']);

export function setupLighting(scene,renderer){
 const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();
 const environment=pmrem.fromScene(room,.035);scene.environment=environment.texture;scene.environmentIntensity=.46;room.dispose();pmrem.dispose();
 scene.background=new THREE.Color('#080d13');
 scene.add(new THREE.HemisphereLight(0xfff9ef,0x292c2b,.2));
 const lights=[];
 for(const z of [-7,-3.5,0,3.5,7]){
  const lamp=new THREE.SpotLight(0xfff5e4,5.8,8,1.35,.85,2);lamp.position.set(0,3.04,z);lamp.target.position.set(0,1,z);scene.add(lamp,lamp.target);lights.push(lamp);
 }
 const fill=new THREE.DirectionalLight(0xffffff,.12);fill.position.set(1,5,2);scene.add(fill);
 // A suggestive station backdrop, not a reconstruction of a particular station.
 const hall=new THREE.Group();
 const wallMat=new THREE.MeshStandardMaterial({color:0x202a34,roughness:.87,envMapIntensity:.08});
 const pillarMat=new THREE.MeshStandardMaterial({color:0x303b45,roughness:.7,envMapIntensity:.08});
 const platformMat=new THREE.MeshStandardMaterial({color:0x232a31,roughness:.8,envMapIntensity:.06});
 const seamMat=new THREE.MeshStandardMaterial({color:0x10171e,roughness:1,envMapIntensity:.02});
 const fixtureMat=new THREE.MeshStandardMaterial({color:0xe0ecf4,emissive:0xc5def0,emissiveIntensity:4,roughness:.35});
 const trimMat=new THREE.MeshStandardMaterial({color:0x45515a,metalness:.5,roughness:.35,envMapIntensity:.12});
 const box=(size,position,material)=>{const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),material);mesh.position.set(...position);hall.add(mesh);return mesh;};
 for(const side of [-1,1]){
  box([.18,5.8,50],[side*6.8,3,0],wallMat);
  box([5,.18,50],[side*4.1,1.02,0],platformMat);
  box([5,.12,50],[side*4.1,4.6,0],seamMat);
  box([.09,.01,50],[side*1.95,1.12,0],new THREE.MeshStandardMaterial({color:0x857549,roughness:.8,envMapIntensity:.06}));
  for(let z=-21;z<=21;z+=3.5){
   box([.35,3.5,.48],[side*4.25,2.84,z],pillarMat);
   box([.012,2.6,.024],[side*6.695,2.7,z],seamMat);
  }
  for(const y of [1.55,2.5,3.45])box([.014,.025,50],[side*6.69,y,0],seamMat);
  box([.08,.1,48],[side*6.65,2.3,0],trimMat);
  for(const z of [-6,5]){
   // Local lights have a short range: station pools remain separated by darkness.
   box([.13,.06,1.35],[side*5.25,3.88,z],fixtureMat);
   box([.22,.045,1.48],[side*5.25,3.935,z],trimMat);
   const lamp=new THREE.PointLight(0xc5def0,13,3.5,2);lamp.position.set(side*5.25,3.7,z);hall.add(lamp);
   // A small illuminated wall panel makes the station legible through the windows.
   box([.018,.085,.7],[side*6.68,2.9,z],fixtureMat);
  }
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
   if(CEILING_LAMPS.has(mat.name)){
    mat.color.set('#fff8ec');mat.emissive.set('#fff5df');mat.emissiveIntensity=3;mat.metalness=0;mat.roughness=.4;
   }else if(name.includes('glass')){
    next=new THREE.MeshPhysicalMaterial({name:mat.name,color:0xffffff,roughness:.025,metalness:0,transmission:.98,thickness:.008,ior:1.46,envMapIntensity:.22,side:THREE.FrontSide});
    next.depthWrite=false;
   }else if(name.startsWith('fabric')){
    mat.color.set('#25292d');mat.metalness=.08;mat.roughness=.72;
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
