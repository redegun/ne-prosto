import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export function createEffects(renderer,scene,camera){
 let outside=false;
 const target=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,samples:2});
 const composer=new EffectComposer(renderer,target);
 composer.addPass(new RenderPass(scene,camera));
 const ao=new GTAOPass(scene,camera,1,1,undefined,{radius:.22,thickness:.12,distanceFallOff:.6,samples:8},{samples:8,radius:4});
 ao.blendIntensity=.65;composer.addPass(ao);

 // Only a thin visible silhouette changes on hover; the original surfaces keep their colour.
 const mask=new THREE.WebGLRenderTarget(1,1,{minFilter:THREE.LinearFilter,magFilter:THREE.LinearFilter});
 const white=new THREE.MeshBasicMaterial({color:0xffffff,side:THREE.DoubleSide,toneMapped:false,fog:false});
 const black=new THREE.MeshBasicMaterial({color:0x000000,side:THREE.DoubleSide,toneMapped:false,fog:false});
 const outline=new ShaderPass({
  uniforms:{tDiffuse:{value:null},maskTexture:{value:null},pixel:{value:new THREE.Vector2(1,1)}},
  vertexShader:'varying vec2 vUv; void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
  fragmentShader:[
   'uniform sampler2D tDiffuse,maskTexture;uniform vec2 pixel;varying vec2 vUv;',
   'void main(){',
   'vec4 base=texture2D(tDiffuse,vUv);float inside=texture2D(maskTexture,vUv).r;',
   'float nearby=max(max(texture2D(maskTexture,vUv+vec2(pixel.x,0.)).r,texture2D(maskTexture,vUv-vec2(pixel.x,0.)).r),',
   'max(texture2D(maskTexture,vUv+vec2(0.,pixel.y)).r,texture2D(maskTexture,vUv-vec2(0.,pixel.y)).r));',
   'float edge=smoothstep(.08,.75,max(0.,nearby-inside));',
   'gl_FragColor=vec4(mix(base.rgb,vec3(.64,.73,.72),edge*.8),base.a);}'
  ].join('\n')
 });
 outline.uniforms.maskTexture.value=mask.texture;
 outline.enabled=false;composer.addPass(outline);composer.addPass(new OutputPass());
 const selected=new Set(),saved=new Map(),clearColor=new THREE.Color();
 function renderMask(){
  const background=scene.background,override=scene.overrideMaterial,renderTarget=renderer.getRenderTarget(),alpha=renderer.getClearAlpha();
  renderer.getClearColor(clearColor);
  try{
   scene.background=null;scene.overrideMaterial=null;
   scene.traverse(o=>{if(o.isMesh){saved.set(o,o.material);o.material=selected.has(o)?white:black;}});
   renderer.setRenderTarget(mask);renderer.setClearColor(0x000000,1);renderer.clear();renderer.render(scene,camera);
  }finally{
   for(const [o,material] of saved)o.material=material;saved.clear();
   scene.background=background;scene.overrideMaterial=override;renderer.setRenderTarget(renderTarget);renderer.setClearColor(clearColor,alpha);
  }
 }

 return {
  setMode(mode){outside=mode==='outside';ao.enabled=!outside;selected.clear();outline.enabled=false;},
  setHighlight(root){selected.clear();root?.traverse(o=>{if(o.isMesh)selected.add(o);});outline.enabled=selected.size>0&&!ao.enabled;},
  render(){if(outside&&!outline.enabled){renderer.render(scene,camera);return;}if(outline.enabled)renderMask();composer.render();},
  resize(width,height){composer.setPixelRatio(renderer.getPixelRatio());composer.setSize(width,height);mask.setSize(width,height);outline.uniforms.pixel.value.set(1.25/width,1.25/height);const ratio=Math.min(renderer.getPixelRatio(),1);ao.setSize(Math.max(1,Math.round(width*ratio)),Math.max(1,Math.round(height*ratio)));}
 };
}
