(() => {
  const root=document.documentElement, button=document.querySelector('.np-menu-toggle'), nav=document.querySelector('.np-nav');
  if(button&&nav){
    root.classList.add('np-js');button.hidden=false;
    const close=()=>{nav.removeAttribute('data-open');button.setAttribute('aria-expanded','false');button.lastElementChild.textContent='+';};
    button.addEventListener('click',()=>{const open=button.getAttribute('aria-expanded')!=='true';button.setAttribute('aria-expanded',String(open));nav.toggleAttribute('data-open',open);button.lastElementChild.textContent=open?'−':'+';});
    nav.addEventListener('click',e=>{if(e.target.closest('a'))close();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&button.getAttribute('aria-expanded')==='true'){close();button.focus();}});
    matchMedia('(min-width:1101px)').addEventListener('change',e=>{if(e.matches)close();});
    nav.querySelectorAll('a').forEach(link=>{const target=new URL(link.href).pathname,path=location.pathname;if(path===target||(target.endsWith('/')&&path.startsWith(target)))link.setAttribute('aria-current',path===target?'page':'true');});
  }
  document.querySelectorAll('.np-site .request-form').forEach(form=>{
    form.addEventListener('invalid',e=>e.target.setAttribute('aria-invalid','true'),true);
    form.addEventListener('input',e=>{if(e.target.validity?.valid)e.target.removeAttribute('aria-invalid');});
    const file=form.querySelector('input[type=file]');
    if(file)file.addEventListener('change',()=>{const label=file.closest('label')?.querySelector('span');if(label)label.textContent=file.files.length?Array.from(file.files).map(x=>x.name).join(', '):'Прикрепить файл';});
  });
  document.querySelectorAll('.np-site .np-presentation img,.np-site .process-wrapper>img').forEach(img=>{img.decoding='async';if(!img.loading)img.loading='lazy';});
})();