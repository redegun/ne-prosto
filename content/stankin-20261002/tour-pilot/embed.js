document.querySelectorAll('[data-stankin-tour]').forEach(link=>{
 const section=link.closest('#tour')||link.parentElement;
 const fit=()=>section.style.setProperty('--st-tour-page-width',document.documentElement.clientWidth+'px');
 fit();window.addEventListener('resize',fit,{passive:true});
 let started=false,visible=false,observer;
 const start=(manual=false)=>{
  if(started)return;
  started=true;observer?.disconnect();
  document.removeEventListener('visibilitychange',resume);
  link.removeEventListener('click',activate);
  const frame=document.createElement('iframe');
  frame.className='st-tour-frame';frame.dataset.view='outside';
  frame.title='3D-просмотр по восьми вагонам поезда СТАНКИН';
  const url=new URL(link.href);
  url.searchParams.set('embed','1');url.searchParams.set('v','20261018-autostart1');
  if(new URLSearchParams(location.search).has('profile'))url.searchParams.set('profile','1');
  frame.src=url.href;frame.allow='fullscreen';frame.allowFullscreen=true;
  window.addEventListener('message',event=>{
   if(event.source!==frame.contentWindow||event.origin!==url.origin||event.data?.type!=='stankin:mode')return;
   frame.dataset.view=event.data.mode==='outside'?'outside':'inside';
  });
  link.replaceWith(frame);
  // Scrolling into the viewer must not move keyboard focus or scroll position.
  if(manual)frame.focus({preventScroll:true});
 };
 const resume=()=>{if(visible&&!document.hidden)start();};
 const activate=event=>{
  if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
  event.preventDefault();start(true);
 };
 link.addEventListener('click',activate);
 if('IntersectionObserver' in window){
  observer=new IntersectionObserver(entries=>{
   visible=entries.some(entry=>entry.isIntersecting&&entry.intersectionRatio>=.1);
   resume();
  },{threshold:.1});
  observer.observe(link);
  document.addEventListener('visibilitychange',resume);
 }
});
