import { createEffects } from './effects.js?v=station2';
import { DetailTextures } from './detail-textures.js?v=station2';
import { improveMaterials, setupLighting } from './appearance.js?v=station2';
import { createStation } from './station.js?v=station2';
import { TrainOverview, disposeTree } from './train-overview.js?v=station2';
import * as THREE from 'three';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const $=id=>document.getElementById(id),host=$('canvas'),viewer=document.querySelector('.viewer');
const keys=new Set(),held=new Set(),pointers=new Set();
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const draco=new DRACOLoader().setDecoderPath('./vendor/draco/').setWorkerLimit(2);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(58,1,.025,650);
let renderer,effects,lighting,controls,station,floor,model,overview,details;
let mode='outside',currentCar=1,busy=false,ready=false,step=0,yaw=0,pitch=0,drag=null,pickStart=null;
let transition=null,lastTime=0,zoomed=false,lastRequest={mode:'outside',car:1};
const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();
const outsideHint='Нажмите на вагон, чтобы войти. Потяните — вращение; колесо и W/S — ближе/дальше; A/D — вдоль поезда.';
const stops=[
 {title:'Вход в салон',p:[0,2.12,6],t:[0,2.12,0]},
 {title:'Оформление левой стены',p:[0,2.12,3.5],t:[-1.25,2.1,1]},
 {title:'Центр вагона',p:[0,2.12,0],t:[1.2,2.1,-1.8]},
 {title:'Оформление у дверей',p:[0,2.12,-3.5],t:[-1.25,2.1,-4.8]},
 {title:'Взгляд вдоль салона',p:[0,2.12,-5.8],t:[0,2.12,6]}
];
const v=a=>new THREE.Vector3(...a);
function syncAngles(){const d=new THREE.Vector3();camera.getWorldDirection(d);pitch=Math.asin(THREE.MathUtils.clamp(d.y,-1,1));yaw=Math.atan2(-d.x,-d.z);}
function look(){camera.rotation.order='YXZ';camera.rotation.set(pitch,yaw,0);const d=new THREE.Vector3();camera.getWorldDirection(d);controls.target.copy(camera.position).add(d);}
function view(p,t,animate=true){
 keys.clear();held.clear();const target=v(t);
 if(animate&&!reduced)transition={from:camera.position.clone(),to:v(p),fromTarget:controls.target.clone(),target,start:performance.now()};
 else{transition=null;camera.position.copy(v(p));controls.target.copy(target);camera.lookAt(target);syncAngles();}
}
function setZoom(enabled){
 zoomed=enabled;camera.fov=enabled?28:mode==='outside'?45:58;camera.updateProjectionMatrix();
 $('zoom').textContent=enabled?'Общий вид':'Ближе';$('zoom').setAttribute('aria-pressed',String(enabled));
}
function fitOutside(animate=false){
 if(!overview)return;
 // A broadside view gives each carriage comparable size and a useful click target.
 const box=new THREE.Box3().setFromObject(overview.root),target=box.getCenter(new THREE.Vector3());
 target.y=2.4;
 const direction=new THREE.Vector3(1,.34,.35).normalize();
 const right=new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0),direction).normalize();
 const up=new THREE.Vector3().crossVectors(direction,right).normalize();
 const tanV=Math.tan(THREE.MathUtils.degToRad(camera.fov*.5)),tanH=tanV*camera.aspect;
 // Keep the orbit anchor on the train; fit distance rather than moving the anchor far away.
 box.min.x=-3.5;box.max.x=9.8;box.min.y=-.4;box.max.y=6.2;
 let distance=8;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
  const p=new THREE.Vector3(x,y,z).sub(target),depth=p.dot(direction);
  distance=Math.max(distance,depth+Math.abs(p.dot(right))/(tanH*.94),depth+Math.abs(p.dot(up))/(tanV*.55));
 }
 controls.maxDistance=Math.max(450,distance*1.5);
 camera.far=Math.max(650,distance*2);camera.updateProjectionMatrix();
 // A portrait overview needs more distance; do not fade its graphics into the background.
 if(scene.fog){scene.fog.near=Math.max(180,distance*1.25);scene.fog.far=Math.max(550,distance*3);}
 view(target.clone().addScaledVector(direction,distance*1.02).toArray(),target.toArray(),animate);
}
function focusOrbit(){
 if(!ready||mode!=='outside'||!overview)return;
 transition=null;
 camera.updateMatrixWorld();overview.root.updateMatrixWorld(true);
 ray.setFromCamera(new THREE.Vector2(0,0),camera);
 const hit=ray.intersectObjects(overview.cars,true)[0];
 let target=hit?.point;
 if(!target){
  // The vertical train plane also handles a centre ray passing through a window/gap.
  const point=ray.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(1,0,0),0),new THREE.Vector3());
  if(point&&Math.abs(point.z)<86&&point.y>.2&&point.y<7)target=point;
 }
 // Both points lie on the existing view ray, so the view does not jump.
 if(target&&target.distanceTo(camera.position)>=controls.minDistance)controls.target.copy(target);
}
function moveOutside(forward,right,dt){
 const offset=camera.position.clone().sub(controls.target),distance=offset.length();
 if(forward)camera.position.copy(controls.target).addScaledVector(offset,THREE.MathUtils.clamp(distance*Math.exp(-forward*dt*1.15),controls.minDistance,controls.maxDistance)/distance);
 if(right){
  // Translate along the train in the screen's left/right direction.
  const screenRight=new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,0);
  const dz=(screenRight.z<0?-1:1)*right*dt*THREE.MathUtils.clamp(distance*.5,5,65);
  const next=THREE.MathUtils.clamp(controls.target.z+dz,-82,82),delta=next-controls.target.z;
  controls.target.z=next;camera.position.z+=delta;
 }
 controls.update();
}
function resize(){
 if(!renderer)return;const box=host.getBoundingClientRect();if(!box.width||!box.height)return;
 renderer.setSize(box.width,box.height,false);camera.aspect=box.width/box.height;camera.updateProjectionMatrix();
 effects?.resize(box.width,box.height);if(ready&&mode==='outside')fitOutside(false);
}
function updateControls(){
 document.querySelectorAll('.modes button').forEach(b=>{b.disabled=!ready;b.setAttribute('aria-pressed',String(b.id===mode));});
 $('reset').disabled=!ready;$('zoom').disabled=!ready;$('car').disabled=busy;
 $('walk').hidden=!ready||mode!=='inside';$('route').hidden=!ready||mode!=='guided';
 $('train-cars').hidden=!ready||mode!=='outside';
 $('car').value=String(currentCar);
 document.querySelectorAll('[data-car]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.car)===currentCar)));
 $('car-status').textContent=mode==='outside'?'Весь поезд · 8 вагонов':'Вагон '+String(currentCar).padStart(2,'0')+' · внутри';
 $('car-label').textContent=mode==='outside'?'Войти в вагон':'Выберите вагон';
}
function setupMode(next){
 mode=next;lighting.setMode(next);effects.setMode(next);station.visible=next==='outside';floor.visible=next!=='outside';
 scene.fog=next==='outside'?new THREE.Fog('#080d13',180,550):null;
 camera.near=next==='outside'?.15:.025;camera.updateProjectionMatrix();
 controls.enabled=ready&&next==='outside';controls.enablePan=next==='outside';
 controls.minDistance=next==='outside'?8:3;
 controls.minPolarAngle=next==='outside'?Math.PI*.14:0;
 controls.maxPolarAngle=Math.PI*.48;
 host.style.cursor=next==='outside'?'grab':'grab';
}
function showStep(animate=true){const s=stops[step];view(s.p,s.t,animate);$('step').textContent=String(step+1).padStart(2,'0')+' / 05';$('stop-title').textContent=s.title;$('prev').disabled=step===0;$('next').disabled=step===4;}
function applyMode(next,animate=true){
 setupMode(next);setZoom(false);updateControls();
 if(next==='outside'){fitOutside(animate);$('hint').textContent=outsideHint;}
 if(next==='inside'){view([0,2.12,6],[0,2.12,0],animate);$('hint').textContent='Потяните, чтобы осмотреться. Для движения — стрелки на экране или клавиши WASD.';}
 if(next==='guided'){step=0;showStep(animate);$('hint').textContent='Переключайте точки стрелками. Потяните, чтобы осмотреться на остановке.';}
}
function clearAssets(){
 details?.dispose();details=null;
 if(model){scene.remove(model);disposeTree(model);model=null;}
 if(overview){scene.remove(overview.root);overview.dispose();overview=null;}
}
function error(message){
 ready=false;controls.enabled=false;$('loading').hidden=false;$('progress').hidden=true;
 document.querySelector('.loading-title').textContent='Не удалось открыть '+(mode==='outside'?'поезд':'вагон');
 $('load-text').textContent=message;$('retry').hidden=false;updateControls();
}
async function open(next,car=currentCar){
 if(busy)return;
 lastRequest={mode:next,car};
 if(ready&&car===currentCar&&((next==='outside'&&overview)||(next!=='outside'&&model))){applyMode(next);return;}
 busy=true;ready=false;currentCar=car;transition=null;drag=null;pickStart=null;keys.clear();held.clear();pointers.clear();
 clearAssets();setupMode(next);updateControls();
 $('loading').hidden=false;$('retry').hidden=true;$('progress').hidden=false;$('progress').value=0;
 document.querySelector('.loading-title').textContent=next==='outside'?'Загружаем весь поезд':'Загружаем вагон '+car;
 $('load-text').textContent='Подготовка модели…';
 try{
  if(next==='outside'){
   overview=new TrainOverview(renderer,draco);scene.add(overview.root);
   await overview.load(done=>{$('progress').value=done/8*100;$('load-text').textContent='Готово вагонов: '+done+' из 8';});
  }else{
   const gltf=await new GLTFLoader().setDRACOLoader(draco).loadAsync('./models/car-'+car+'.glb?v=20261008-draco',e=>{
    if(e.total){const p=Math.round(e.loaded/e.total*100);$('progress').value=p;$('load-text').textContent=p===100?'Открываем оформление…':'Загружено '+p+'%';}
   });
   model=gltf.scene;improveMaterials(model);
   const center=new THREE.Box3().setFromObject(model).getCenter(new THREE.Vector3());model.position.x-=center.x;model.position.z-=center.z;
   model.traverse(o=>{if(o.isMesh)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{if(m.map)m.map.anisotropy=Math.min(16,renderer.capabilities.getMaxAnisotropy());});});
   scene.add(model);details=new DetailTextures(renderer,model,car);$('load-text').textContent='Подключаем оформление…';await details.ready;
  }
  ready=true;$('loading').hidden=true;applyMode(next,false);
  if(document.activeElement===document.body||viewer.contains(document.activeElement))host.focus({preventScroll:true});
 }catch(e){clearAssets();error('Проверьте соединение и попробуйте ещё раз. Можно также выбрать вагон в списке.');console.error(e);}
 finally{busy=false;updateControls();}
}
function move(forward,right,dt){
 const speed=dt*1.7,dx=(-Math.sin(yaw)*forward+Math.cos(yaw)*right)*speed,dz=(-Math.cos(yaw)*forward-Math.sin(yaw)*right)*speed;
 camera.position.x=THREE.MathUtils.clamp(camera.position.x+dx,-.43,.43);
 camera.position.z=THREE.MathUtils.clamp(camera.position.z+dz,currentCar===8?-6:-8.1,currentCar===1?6:8.1);
 camera.position.y=2.12;look();
}
function frame(now){
 if(!renderer)return;
 const dt=Math.min((now-lastTime)/1000,.05);lastTime=now;
 if(transition){
  const a=THREE.MathUtils.clamp((now-transition.start)/650,0,1),e=a*a*(3-2*a);
  camera.position.lerpVectors(transition.from,transition.to,e);controls.target.lerpVectors(transition.fromTarget,transition.target,e);camera.lookAt(controls.target);
  if(a===1){transition=null;syncAngles();}
 }else if(ready&&mode==='outside'){
  const f=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown'));
  const r=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  if(f||r)moveOutside(f,r,dt);else controls.update();
 }
 else if(ready&&mode==='inside'){
  const f=Number(keys.has('KeyW')||keys.has('ArrowUp')||held.has('forward'))-Number(keys.has('KeyS')||keys.has('ArrowDown')||held.has('back'));
  const r=Number(keys.has('KeyD')||keys.has('ArrowRight')||held.has('right'))-Number(keys.has('KeyA')||keys.has('ArrowLeft')||held.has('left'));
  if(f||r)move(f,r,dt);
 }
 if(ready&&!transition)details?.update(now,camera);
 effects.render();requestAnimationFrame(frame);
}
function pickedCar(e){
 if(!overview)return 0;
 const rect=host.getBoundingClientRect();pointer.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);
 camera.updateMatrixWorld();overview.root.updateMatrixWorld(true);ray.setFromCamera(pointer,camera);
 const direct=ray.intersectObjects(overview.cars,true)[0]?.object.userData.car;
 if(direct)return direct;
 // At full-train scale the body is thin: allow a 44 px high hit area around each car.
 let nearest=0,best=Infinity;
 for(const car of overview.cars){
  const box=car.userData.pickBox||(car.userData.pickBox=new THREE.Box3().setFromObject(car));
  let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity,visible=false;
  for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
   const p=new THREE.Vector3(x,y,z).project(camera);if(p.z<-1||p.z>1)continue;visible=true;
   const sx=rect.left+(p.x+1)*rect.width/2,sy=rect.top+(1-p.y)*rect.height/2;
   x0=Math.min(x0,sx);x1=Math.max(x1,sx);y0=Math.min(y0,sy);y1=Math.max(y1,sy);
  }
  if(!visible)continue;
  const cy=(y0+y1)/2,pad=Math.max(0,(44-(y1-y0))/2);
  if(e.clientX<x0-2||e.clientX>x1+2||e.clientY<y0-pad||e.clientY>y1+pad)continue;
  const distance=Math.hypot((e.clientX-(x0+x1)/2)/Math.max(1,x1-x0),(e.clientY-cy)/Math.max(44,y1-y0));
  if(distance<best){best=distance;nearest=car.userData.car;}
 }
 return nearest;
}
function highlightCar(car){
 if(mode!=='outside')return;
 overview?.highlight(car);host.style.cursor=car?'pointer':'grab';
 $('hint').textContent=car?'Вагон '+String(car).padStart(2,'0')+' · Нажмите, чтобы войти':outsideHint;
}
try{
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});
 renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
 renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.9;host.appendChild(renderer.domElement);
 controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.screenSpacePanning=true;controls.rotateSpeed=.55;
 lighting=setupLighting(scene,renderer);station=createStation(180);scene.add(station);
 floor=new THREE.Mesh(new THREE.PlaneGeometry(150,150),new THREE.MeshStandardMaterial({color:0x10151b,roughness:1,envMapIntensity:.05}));
 floor.rotation.x=-Math.PI/2;floor.position.y=-.12;scene.add(floor);
 effects=createEffects(renderer,scene,camera);resize();new ResizeObserver(resize).observe(host);
 renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();error('Графический режим остановлен. Нажмите «Попробовать ещё раз», чтобы перезагрузить просмотр.');});
 requestAnimationFrame(frame);open('outside');
}catch(e){$('loading').hidden=false;document.querySelector('.loading-title').textContent='3D-просмотр недоступен';$('load-text').textContent='Откройте кейс с фотографиями или попробуйте другой браузер.';console.error(e);}
['outside','inside','guided'].forEach(m=>$(m).onclick=()=>open(m));
$('reset').onclick=()=>applyMode(mode);$('zoom').onclick=()=>{if(ready){if(mode==='outside')focusOrbit();setZoom(!zoomed);}};
$('prev').onclick=()=>{if(step>0){step--;showStep();}};$('next').onclick=()=>{if(step<4){step++;showStep();}};
$('retry').onclick=()=>renderer&&!renderer.getContext().isContextLost()?open(lastRequest.mode,lastRequest.car):location.reload();
$('car').onchange=()=>open('inside',Number($('car').value));
document.querySelectorAll('[data-car]').forEach(b=>{
 const car=Number(b.dataset.car);b.onclick=()=>open('inside',car);
 b.addEventListener('pointerenter',()=>highlightCar(car));b.addEventListener('pointerleave',()=>highlightCar(0));
 b.addEventListener('focus',()=>highlightCar(car));b.addEventListener('blur',()=>highlightCar(0));
});
$('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else if(viewer.requestFullscreen)await viewer.requestFullscreen();else $('hint').textContent='Полноэкранный режим недоступен в этом браузере.';}catch{$('hint').textContent='Полноэкранный режим недоступен в этом браузере.';}};
document.addEventListener('fullscreenchange',()=>{$('fullscreen').textContent=document.fullscreenElement?'Свернуть':'На весь экран';$('fullscreen').setAttribute('aria-label',document.fullscreenElement?'Выйти из полноэкранного режима':'Открыть на весь экран');resize();});
host.addEventListener('pointerdown',()=>{
 if(ready&&mode==='outside'){host.focus({preventScroll:true});if(!pointers.size)focusOrbit();}
},true);
host.addEventListener('wheel',()=>{if(ready&&mode==='outside')focusOrbit();},{capture:true,passive:true});
host.addEventListener('pointerdown',e=>{
 if(!ready||transition)return;
 pointers.add(e.pointerId);
 if(mode==='outside'){
  pickStart=pointers.size===1&&e.button===0?{id:e.pointerId,x:e.clientX,y:e.clientY}:null;
  return;
 }
 host.focus({preventScroll:true});host.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY};
});
host.addEventListener('pointermove',e=>{
 if(mode==='outside'){
  if(pickStart&&Math.hypot(e.clientX-pickStart.x,e.clientY-pickStart.y)>7)pickStart=null;
  if(ready&&!pointers.size&&e.pointerType==='mouse')highlightCar(pickedCar(e));
  return;
 }
 if(!drag)return;yaw-=(e.clientX-drag.x)*.004;pitch=THREE.MathUtils.clamp(pitch-(e.clientY-drag.y)*.003,-1.05,1.05);
 drag={x:e.clientX,y:e.clientY};look();
});
host.addEventListener('pointerup',e=>{
 pointers.delete(e.pointerId);
 if(mode==='outside'&&pickStart?.id===e.pointerId&&!pointers.size){
  const car=pickedCar(e);pickStart=null;if(car)open('inside',car);
 }
 pickStart=null;drag=null;
});
host.addEventListener('pointerleave',()=>{if(mode==='outside'&&ready)highlightCar(0);});
['pointercancel','lostpointercapture'].forEach(n=>host.addEventListener(n,e=>{pointers.delete(e.pointerId);pickStart=null;drag=null;}));
viewer.addEventListener('keydown',e=>{
 if(!ready||transition)return;
 if(mode==='outside'&&e.code==='Enter'&&(e.target===host||e.target===renderer.domElement)){e.preventDefault();open('inside',currentCar);return;}
 if((mode==='inside'||mode==='outside')&&['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)){
  e.preventDefault();if(!e.repeat){if(mode==='outside')focusOrbit();const f=['KeyW','ArrowUp'].includes(e.code)?1:['KeyS','ArrowDown'].includes(e.code)?-1:0,r=['KeyD','ArrowRight'].includes(e.code)?1:['KeyA','ArrowLeft'].includes(e.code)?-1:0;if(mode==='outside')moveOutside(f,r,.08);else move(f,r,.08);}keys.add(e.code);
 }
 if(mode==='guided'&&e.code==='ArrowRight'&&step<4){e.preventDefault();step++;showStep();}
 if(mode==='guided'&&e.code==='ArrowLeft'&&step>0){e.preventDefault();step--;showStep();}
});
window.addEventListener('keyup',e=>keys.delete(e.code));
host.addEventListener('blur',()=>{keys.clear();held.clear();});
window.addEventListener('blur',()=>{keys.clear();held.clear();drag=null;pickStart=null;pointers.clear();});
document.querySelectorAll('[data-move]').forEach(b=>{
 let downAt=0;
 const nudge=()=>{if(mode!=='inside'||transition||!ready)return;const m=b.dataset.move;move(m==='forward'?1:m==='back'?-1:0,m==='right'?1:m==='left'?-1:0,.3);};
 b.addEventListener('pointerdown',e=>{e.preventDefault();if(transition||!ready)return;b.setPointerCapture(e.pointerId);downAt=performance.now();held.add(b.dataset.move);});
 b.addEventListener('pointerup',()=>{if(downAt&&performance.now()-downAt<160)nudge();downAt=0;held.delete(b.dataset.move);});
 ['pointercancel','lostpointercapture'].forEach(n=>b.addEventListener(n,()=>{downAt=0;held.delete(b.dataset.move);}));
 b.addEventListener('click',e=>{if(e.detail===0)nudge();});
});
