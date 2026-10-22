
/* task 538: призывы в статье — открытие формы и ответ AjaxForm внутри своего блока */
(function(){
  if(!document.body||!document.querySelector('.np-cta'))return;
  [].forEach.call(document.querySelectorAll('.np-cta__details'),function(d){
    d.addEventListener('toggle',function(){if(d.open&&window.matchMedia('(hover:hover)').matches){var f=d.querySelector('input[name=name]');if(f)try{f.focus({preventScroll:true})}catch(e){f.focus()}}});
  });
  if(!window.jQuery)return;
  jQuery(document).on('af_complete',function(e,r){
    var form=r&&r.form&&r.form[0];if(!form||!form.classList.contains('np-cta-form'))return;
    var box=form.closest('.np-cta'),out=box&&box.querySelector('.np-cta__result');if(!out)return;
    out.textContent=String(r.message||'').replace(/<[^>]*>/g,' ').replace(/&nbsp;/g,' ').replace(/\s+/g,' ').trim();
    out.classList.toggle('is-error',!r.success);
    if(r.success)box.classList.add('is-sent');
  });
})();
