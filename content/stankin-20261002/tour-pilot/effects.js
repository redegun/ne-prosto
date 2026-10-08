import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export function createEffects(renderer,scene,camera){
 const mobile=matchMedia('(max-width:720px)').matches;
 const target=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,samples:mobile?2:4});
 const composer=new EffectComposer(renderer,target);
 composer.addPass(new RenderPass(scene,camera));
 const ao=new GTAOPass(scene,camera,1,1,undefined,{radius:.22,thickness:.12,distanceFallOff:.6,samples:8},{samples:8,radius:4});
 ao.blendIntensity=.65;composer.addPass(ao);
 composer.addPass(new OutputPass());
 return {
  render(){composer.render();},
  resize(width,height){composer.setSize(width,height);const ratio=Math.min(renderer.getPixelRatio(),1);ao.setSize(Math.max(1,Math.round(width*ratio)),Math.max(1,Math.round(height*ratio)));}
 };
}
