document.querySelectorAll('[data-stankin-tour]').forEach(link=>{
 const section=link.closest('#tour')||link.parentElement;
 const fit=()=>section.style.setProperty('--st-tour-page-width',document.documentElement.clientWidth+'px');
 fit();window.addEventListener('resize',fit,{passive:true});
 link.addEventListener('click',event=>{
  if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
  event.preventDefault();
  const frame=document.createElement('iframe');
  frame.className='st-tour-frame';frame.dataset.view='outside';
  frame.title='3D-просмотр по восьми вагонам поезда СТАНКИН';
  frame.src=link.href+'?embed=1&v=20261018-screen1'+(new URLSearchParams(location.search).has('profile')?'&profile=1':'');frame.allow='fullscreen';frame.allowFullscreen=true;
  const origin=new URL(frame.src).origin;
  window.addEventListener('message',event=>{
   if(event.source!==frame.contentWindow||event.origin!==origin||event.data?.type!=='stankin:mode')return;
   frame.dataset.view=event.data.mode==='outside'?'outside':'inside';
  });
  link.replaceWith(frame);frame.focus();
 },{once:true});
});
