document.querySelectorAll('[data-stankin-tour]').forEach(link=>{
 link.addEventListener('click',event=>{
  if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
  event.preventDefault();
  const frame=document.createElement('iframe');
  frame.className='st-tour-frame';frame.title='3D-экскурсия по восьми вагонам поезда СТАНКИН';
  frame.src=link.href+'?embed=1';frame.allow='fullscreen';frame.allowFullscreen=true;
  link.replaceWith(frame);frame.focus();
 });
});