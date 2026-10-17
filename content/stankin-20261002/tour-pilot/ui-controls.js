// Hide visual chrome without removing keyboard or assistive-technology access.
export function setupAutoHideControls(viewer) {
 const surfaces=viewer.querySelectorAll('.modes,.view-actions,.tools-toggle,.outside-nav,.walk,.route,.hint');
 surfaces.forEach(el=>el.dataset.tourControls='');
 const controlSelector='[data-tour-controls]';
 const activePointers=new Set(),wakingTouches=new Set();
 let timer=0,keyboard=false;
 const delay=2400;
 function blocked(){
  const focus=document.activeElement;
  return !viewer.querySelector('#loading').hidden || activePointers.size ||
   viewer.classList.contains('tools-open') ||
   (keyboard && viewer.contains(focus) && focus.closest(controlSelector));
 }
 function hide(){
  clearTimeout(timer);
  if(blocked()){timer=setTimeout(hide,delay);return;}
  viewer.classList.add('ui-idle');
 }
 function show(){
  viewer.classList.remove('ui-idle');
  clearTimeout(timer);timer=setTimeout(hide,delay);
 }
 viewer.addEventListener('pointermove',show,{passive:true});
 viewer.addEventListener('pointerdown',e=>{
  keyboard=false;
  if(e.pointerType!=='mouse' && viewer.classList.contains('ui-idle'))wakingTouches.add(e.pointerId);
  activePointers.add(e.pointerId);show();
 },true);
 for(const name of ['pointerup','pointercancel'])window.addEventListener(name,e=>{
  if(activePointers.delete(e.pointerId))show();
  wakingTouches.delete(e.pointerId);
 });
 viewer.addEventListener('wheel',show,{passive:true});
 viewer.addEventListener('keydown',()=>{keyboard=true;show();},true);
 viewer.addEventListener('focusin',e=>{if(e.target.matches(':focus-visible'))keyboard=true;show();});
 viewer.addEventListener('focusout',show);
 viewer.addEventListener('click',show);
 document.addEventListener('fullscreenchange',show);
 window.addEventListener('blur',()=>{activePointers.clear();wakingTouches.clear();show();});
 // Loading and menu changes can happen without a pointer/keyboard event.
 new MutationObserver(show).observe(viewer.querySelector('#loading'),{attributes:true,attributeFilter:['hidden']});
 show();
 return {wokeOnTouch:e=>wakingTouches.has(e.pointerId)};
}
