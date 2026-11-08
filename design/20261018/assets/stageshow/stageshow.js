/* task 1726: ролики грузятся при подлёте к экрану, reduced-motion -> постер */
(function(){
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function start(v){
    if (!v.dataset.on) {
      v.poster = v.dataset.poster;
      v.querySelectorAll('source').forEach(function(s){ s.src = s.dataset.src; });
      v.dataset.on = '1'; v.load();
    }
    var p = v.play(); if (p && p.catch) p.catch(function(){});
  }
  function boot(){
    document.querySelectorAll('.np-ss video').forEach(function(v){
      var box = v.parentElement;
      if (getComputedStyle(box).display === 'none') return;
      if (reduce) {
        var i = new Image(); i.src = v.dataset.poster; i.alt = v.getAttribute('aria-label') || '';
        i.loading = 'lazy'; i.decoding = 'async'; i.width = v.width; i.height = v.height; v.replaceWith(i); return;
      }
      if (!('IntersectionObserver' in window)) { start(v); return; }
      var io = new IntersectionObserver(function(es){ es.forEach(function(e){
        if (e.isIntersecting) start(v); else if (v.dataset.on) v.pause();
      }); }, { rootMargin: '200px 0px' });
      io.observe(v);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
