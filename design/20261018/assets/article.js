/* task 520: оглавление статьи блога по H2 */
(function(){
  var body=document.body;
  if(!body||!body.classList.contains('np-article-page'))return;
  var content=document.querySelector('.article-content');
  if(!content||document.querySelector('.np-toc'))return;
  var hs=[].slice.call(content.querySelectorAll('h2')).filter(function(h){return h.textContent.trim()&&!h.closest('form,.np-request,section[class*="request"]')});
  if(hs.length<2)return;
  var map={'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'c','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'};
  var used={};
  function slug(t){
    var s=t.toLowerCase().split('').map(function(c){return map.hasOwnProperty(c)?map[c]:c}).join('').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,60)||'razdel';
    var b=s,i=2;while(used[s]||document.getElementById(s))s=b+'-'+i++;used[s]=1;return s;
  }
  var nav=document.createElement('details');
  nav.className='np-toc'+(hs.some(function(h){return /^\s*\d+[.)]/.test(h.textContent)})?' np-toc--plain':'');
  nav.setAttribute('aria-label','Содержание статьи');
  var sum=document.createElement('summary');sum.textContent='Содержание';nav.appendChild(sum);
  var ol=document.createElement('ol');
  var links=[];
  hs.forEach(function(h){
    if(!h.id)h.id=slug(h.textContent.trim());
    var li=document.createElement('li'),a=document.createElement('a');
    a.href=location.href.split('#')[0]+'#'+h.id;a.textContent=h.textContent.trim().replace(/\s+/g,' ');
    li.appendChild(a);ol.appendChild(li);links.push(a);
  });
  nav.appendChild(ol);
  content.parentNode.insertBefore(nav,content);
  var mq=window.matchMedia('(min-width:1101px)');
  function sync(){nav.open=mq.matches||nav.dataset.userOpen==='1'}
  sync();
  if(mq.addEventListener)mq.addEventListener('change',sync);else if(mq.addListener)mq.addListener(sync);
  sum.addEventListener('click',function(e){if(mq.matches){e.preventDefault();return}nav.dataset.userOpen=nav.open?'0':'1'});
  ol.addEventListener('click',function(e){if(e.target.closest('a')&&!mq.matches){nav.open=false;nav.dataset.userOpen='0'}});
  if('IntersectionObserver' in window){
    var cur=null;
    var io=new IntersectionObserver(function(es){
      es.forEach(function(en){if(en.isIntersecting)cur=en.target});
      var top=null;hs.forEach(function(h){if(h.getBoundingClientRect().top<window.innerHeight*0.35)top=h});
      top=top||cur;
      links.forEach(function(a){a.classList.toggle('is-active',!!top&&a.hash==='#'+top.id)});
    },{rootMargin:'0px 0px -60% 0px'});
    hs.forEach(function(h){io.observe(h)});
  }
})();
