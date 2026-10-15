import { createEffects } from './effects.js?v=exterior2';
import { DetailTextures } from './detail-textures.js?v=exterior2';
import { improveMaterials, setupLighting } from './appearance.js?v=exterior2';
import * as THREE from 'three';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const $=id=>document.getElementById(id);
const host=$('canvas'), viewer=document.querySelector('.viewer');
let lighting,effects,renderer,controls,model,mode='inside',step=0,yaw=0,pitch=0,drag=null,ready=false,transition=null,lastTime=0;
let currentCar=Number($('car').value),loadingCar=false,details=null,zoomed=false;
const keys=new Set(), held=new Set(), reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const draco=new DRACOLoader().setDecoderPath('./vendor/draco/').setWorkerLimit(2);
const scene=new THREE.Scene();scene.background=new THREE.Color(0xe9edf0);
const camera=new THREE.PerspectiveCamera(58,1,.025,250);
const stops=[
 {title:'Вход в салон',p:[0,2.12,6],t:[0,2.12,0]},
 {title:'Оформление левой стены',p:[0,2.12,3.5],t:[-1.25,2.1,1]},
 {title:'Центр вагона',p:[0,2.12,0],t:[1.2,2.1,-1.8]},
 {title:'Оформление у дверей',p:[0,2.12,-3.5],t:[-1.25,2.1,-4.8]},
 {title:'Взгляд вдоль салона',p:[0,2.12,-5.8],t:[0,2.12,6]}
];
const v=a=>new THREE.Vector3(...a);
function error(message){ready=false;$('loading').hidden=false;$('progress').hidden=true;document.querySelector('.loading-title').textContent='Не удалось открыть вагон';$('load-text').textContent=message;$('retry').hidden=false;document.querySelectorAll('.modes button').forEach(b=>b.disabled=true);$('reset').disabled=true;}
function resize(){if(!renderer)return;const box=host.getBoundingClientRect();renderer.setSize(box.width,box.height,false);camera.aspect=box.width/box.height;camera.updateProjectionMatrix();effects?.resize(box.width,box.height);if(ready&&mode==='outside')frameOutside(false);}
function view(p,t,animate=true){keys.clear();held.clear();const target=v(t);if(animate&&!reduced){transition={from:camera.position.clone(),to:v(p),fromTarget:controls.target.clone(),target,start:performance.now()};}else{transition=null;camera.position.copy(v(p));controls.target.copy(target);camera.lookAt(target);syncAngles();}}
function syncAngles(){const d=new THREE.Vector3();camera.getWorldDirection(d);pitch=Math.asin(THREE.MathUtils.clamp(d.y,-1,1));yaw=Math.atan2(-d.x,-d.z);}
function look(){camera.rotation.order='YXZ';camera.rotation.set(pitch,yaw,0);const d=new THREE.Vector3();camera.getWorldDirection(d);controls.target.copy(camera.position).add(d);}
function setMode(next,animate=true){if(!ready)return;setZoom(false);mode=next;lighting.setMode(mode);controls.enabled=mode==='outside';controls.enablePan=mode==='outside';document.querySelectorAll('.modes button').forEach(b=>b.setAttribute('aria-pressed',String(b.id===next)));$('walk').hidden=mode!=='inside';$('route').hidden=mode!=='guided';if(mode==='outside'){frameOutside(animate);$('hint').textContent='Потяните, чтобы повернуть вагон. Колёсико или жест двумя пальцами — приближение. Правая кнопка мыши — сдвиг.';}if(mode==='inside'){view([0,2.12,6.0],[0,2.12,0],animate);$('hint').textContent='Потяните, чтобы осмотреться. Для движения — стрелки на экране или клавиши WASD.';}if(mode==='guided'){step=0;showStep(animate);$('hint').textContent='Переключайте точки стрелками. Потяните, чтобы осмотреться на остановке.';}}
function frameOutside(animate=false){
 if(!model)return;
 const box=new THREE.Box3().setFromObject(model),target=box.getCenter(new THREE.Vector3());
 const direction=new THREE.Vector3(12,3.9,13).normalize(),right=new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0),direction).normalize(),up=new THREE.Vector3().crossVectors(direction,right).normalize();
 const tanV=Math.tan(THREE.MathUtils.degToRad(camera.fov*.5)),tanH=tanV*camera.aspect;
 let distance=4;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
  const point=new THREE.Vector3(x,y,z).sub(target),depth=point.dot(direction);
  distance=Math.max(distance,depth+Math.abs(point.dot(right))*1.18/tanH,depth+Math.abs(point.dot(up))*1.4/tanV);
 }
 controls.maxDistance=Math.max(40,distance*1.7);
 view(target.clone().addScaledVector(direction,distance).toArray(),target.toArray(),animate);
}
function showStep(animate=true){const s=stops[step];view(s.p,s.t,animate);$('step').textContent=String(step+1).padStart(2,'0')+' / '+String(stops.length).padStart(2,'0');$('stop-title').textContent=s.title;$('prev').disabled=step===0;$('next').disabled=step===stops.length-1;}
function move(forward,right,dt){const speed=dt*1.7,dx=(-Math.sin(yaw)*forward+Math.cos(yaw)*right)*speed,dz=(-Math.cos(yaw)*forward-Math.sin(yaw)*right)*speed;camera.position.x=THREE.MathUtils.clamp(camera.position.x+dx,-.43,.43);camera.position.z=THREE.MathUtils.clamp(camera.position.z+dz,currentCar===8?-6.0:-8.1,currentCar===1?6.0:8.1);camera.position.y=2.12;look();}
function frame(now){if(!renderer)return;const dt=Math.min((now-lastTime)/1000,.05);lastTime=now;if(transition){const a=THREE.MathUtils.clamp((now-transition.start)/650,0,1),e=a*a*(3-2*a);camera.position.lerpVectors(transition.from,transition.to,e);controls.target.lerpVectors(transition.fromTarget,transition.target,e);camera.lookAt(controls.target);if(a===1){transition=null;syncAngles();}}else if(mode==='outside')controls.update();else if(mode==='inside'){const f=Number(keys.has('KeyW')||keys.has('ArrowUp')||held.has('forward'))-Number(keys.has('KeyS')||keys.has('ArrowDown')||held.has('back')),r=Number(keys.has('KeyD')||keys.has('ArrowRight')||held.has('right'))-Number(keys.has('KeyA')||keys.has('ArrowLeft')||held.has('left'));if(f||r)move(f,r,dt);}if(ready&&!transition)details?.update(now,camera);effects.render();requestAnimationFrame(frame);}
function disposeModel(root){
 const geometries=new Set(),materials=new Set(),textures=new Set();
 root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));});
 materials.forEach(m=>Object.values(m).forEach(value=>{if(value?.isTexture)textures.add(value);}));
 geometries.forEach(g=>g.dispose());textures.forEach(t=>{t.dispose();t.source?.data?.close?.();});materials.forEach(m=>m.dispose());
}
async function load(){
 if(loadingCar)return;
 loadingCar=true;ready=false;transition=null;drag=null;keys.clear();held.clear();controls.enabled=false;
 document.querySelectorAll('.modes button').forEach(b=>b.disabled=true);$('reset').disabled=true;$('car').disabled=true;
 $('walk').hidden=true;$('route').hidden=true;
 details?.dispose();details=null;
 if(model){scene.remove(model);disposeModel(model);model=null;}
 try{
  $('loading').hidden=false;$('retry').hidden=true;$('progress').hidden=false;$('progress').value=0;
  document.querySelector('.loading-title').textContent='Загружаем вагон '+currentCar;
  $('load-text').textContent='Подготовка модели…';
  const gltf=await new GLTFLoader().setDRACOLoader(draco).loadAsync('./models/car-'+currentCar+'.glb?v=20261008-draco',e=>{
   if(e.total){const percent=Math.round(e.loaded/e.total*100);$('progress').value=percent;$('load-text').textContent=percent===100?'Открываем оформление…':'Загружено '+percent+'%';}
  });
  model=gltf.scene;improveMaterials(model);
  const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3());
  model.position.x-=center.x;model.position.z-=center.z;
  model.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=false;const mats=Array.isArray(o.material)?o.material:[o.material];mats.forEach(m=>{if(m.map)m.map.anisotropy=Math.min(16,renderer.capabilities.getMaxAnisotropy());});}});
  scene.add(model);details=new DetailTextures(renderer,model,currentCar);$('load-text').textContent='Подключаем оформление…';await details.ready;ready=true;$('loading').hidden=true;
  document.querySelectorAll('.modes button').forEach(b=>b.disabled=false);$('reset').disabled=false;
  $('car-status').textContent='Вагон '+String(currentCar).padStart(2,'0')+' · оформление поезда';
  setMode(mode,false);
 }catch(e){error('Проверьте соединение и попробуйте ещё раз или выберите другой вагон. Фотографии проекта доступны в основном кейсе.');console.error(e);}
 finally{loadingCar=false;$('car').disabled=false;}
}

try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.9;host.appendChild(renderer.domElement);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.minDistance=3;controls.maxDistance=30;controls.maxPolarAngle=Math.PI*.49;lighting=setupLighting(scene,renderer);const floor=new THREE.Mesh(new THREE.PlaneGeometry(150,150),new THREE.MeshStandardMaterial({color:0x10151b,roughness:1,envMapIntensity:.05}));floor.rotation.x=-Math.PI/2;floor.position.y=-.12;scene.add(floor);effects=createEffects(renderer,scene,camera);resize();new ResizeObserver(resize).observe(host);renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();error('Графический режим остановлен. Нажмите «Попробовать ещё раз», чтобы перезагрузить просмотр.');});requestAnimationFrame(frame);load();}catch(e){error('Ваш браузер не смог запустить 3D. Откройте кейс с фотографиями или попробуйте другой браузер.');}
['outside','inside','guided'].forEach(m=>$(m).onclick=()=>setMode(m));$('reset').onclick=()=>setMode(mode);$('prev').onclick=()=>{if(step>0){step--;showStep();}};$('next').onclick=()=>{if(step<stops.length-1){step++;showStep();}};$('retry').onclick=()=>renderer&&!renderer.getContext().isContextLost()?load():location.reload();
$('car').onchange=()=>{currentCar=Number($('car').value);mode=mode==='outside'?'outside':'inside';load();};
$('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else if(viewer.requestFullscreen)await viewer.requestFullscreen();else{$('hint').textContent='Полноэкранный режим недоступен в этом браузере.';}}catch{$('hint').textContent='Полноэкранный режим недоступен в этом браузере.';}};
document.addEventListener('fullscreenchange',()=>{$('fullscreen').textContent=document.fullscreenElement?'Свернуть':'На весь экран';$('fullscreen').setAttribute('aria-label',document.fullscreenElement?'Выйти из полноэкранного режима':'Открыть на весь экран');resize();});
host.addEventListener('pointerdown',e=>{if(mode==='outside'||!ready||transition)return;host.focus({preventScroll:true});host.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY};});
host.addEventListener('pointermove',e=>{if(!drag)return;yaw-=(e.clientX-drag.x)*.004;pitch=THREE.MathUtils.clamp(pitch-(e.clientY-drag.y)*.003,-1.05,1.05);drag={x:e.clientX,y:e.clientY};look();});
['pointerup','pointercancel','lostpointercapture'].forEach(n=>host.addEventListener(n,()=>drag=null));
host.addEventListener('keydown',e=>{if(mode==='inside'&&['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)){e.preventDefault();if(!e.repeat&&!transition){const f=['KeyW','ArrowUp'].includes(e.code)?1:['KeyS','ArrowDown'].includes(e.code)?-1:0;const r=['KeyD','ArrowRight'].includes(e.code)?1:['KeyA','ArrowLeft'].includes(e.code)?-1:0;move(f,r,.08);}keys.add(e.code);}if(mode==='guided'&&e.code==='ArrowRight'&&step<stops.length-1){e.preventDefault();step++;showStep();}if(mode==='guided'&&e.code==='ArrowLeft'&&step>0){e.preventDefault();step--;showStep();}});
host.addEventListener('keyup',e=>keys.delete(e.code));host.addEventListener('blur',()=>{keys.clear();held.clear();});window.addEventListener('blur',()=>{keys.clear();held.clear();drag=null;});
document.querySelectorAll('[data-move]').forEach(b=>{let downAt=0;const nudge=()=>{if(mode!=='inside'||transition)return;const m=b.dataset.move;move(m==='forward'?1:m==='back'?-1:0,m==='right'?1:m==='left'?-1:0,.3);};b.addEventListener('pointerdown',e=>{e.preventDefault();if(transition)return;b.setPointerCapture(e.pointerId);downAt=performance.now();held.add(b.dataset.move);});b.addEventListener('pointerup',()=>{if(downAt&&performance.now()-downAt<160)nudge();downAt=0;held.delete(b.dataset.move);});['pointercancel','lostpointercapture'].forEach(n=>b.addEventListener(n,()=>{downAt=0;held.delete(b.dataset.move);}));b.addEventListener('click',e=>{if(e.detail===0)nudge();});});
function setZoom(enabled){zoomed=enabled;camera.fov=enabled?28:58;camera.updateProjectionMatrix();$('zoom').textContent=enabled?'Общий вид':'Ближе';$('zoom').setAttribute('aria-pressed',String(enabled));}
$('zoom').onclick=()=>{if(ready)setZoom(!zoomed);};
