/* task 1726: ролики грузятся при подлёте к экрану, reduced-motion -> постер
   task 1746: data-ss-alt="a,b,c" — карточка чередует ролики: случайный первый за показ, дальше по кругу после каждого проигрыша */
(function(){
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function rename(v, from, to){
    v.dataset.poster = v.dataset.poster.split(from).join(to);
    v.querySelectorAll('source').forEach(function(s){ s.dataset.src = s.dataset.src.split(from).join(to); });
    v.dataset.ssCur = to;
  }
  function rotation(v){
    var m = /stageshow\/([^\/]+)\//.exec(v.dataset.poster || '');
    if (!v.dataset.ssAlt || !m) return;
    var list = [m[1]].concat(v.dataset.ssAlt.split(',').filter(Boolean));
    v.dataset.ssCur = m[1];
    var i = Math.floor(Math.random() * list.length);
    if (i) rename(v, m[1], list[i]);
    v.loop = false; v.removeAttribute('loop');
    v.addEventListener('ended', function(){
      var cur = v.dataset.ssCur, next = list[(list.indexOf(cur) + 1) % list.length];
      rename(v, cur, next);
      if (v.dataset.on) {
        v.poster = v.dataset.poster;
        v.querySelectorAll('source').forEach(function(s){ s.src = s.dataset.src; });
        v.load(); var p = v.play(); if (p && p.catch) p.catch(function(){});
      }
    });
  }
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
      rotation(v);
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
