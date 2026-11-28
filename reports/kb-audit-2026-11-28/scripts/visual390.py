import json, re, time
from playwright.sync_api import sync_playwright
OUT="D:/project/tmp/task-5182/evidence"
URLS=["https://ne-prosto.ru/","https://ne-prosto.ru/uslugi/sajtyi","https://ne-prosto.ru/uslugi/ii-assistent-dlya-biznesa","https://ne-prosto.ru/uslugi/","https://ne-prosto.ru/blog/semanticheskoe-yadro-sajta","https://ne-prosto.ru/blog/besplatnye-kirillicheskie-shrifty","https://ne-prosto.ru/portfolio/vinyl-tm","https://ne-prosto.ru/portfolio/","https://ne-prosto.ru/koordinatyi"]
INIT="""window.__lcp=[];try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp.push({t:e.startTime,tag:e.element?e.element.tagName:null,url:e.url,el:e.element});}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}"""
JS=r"""()=>{
const vh=844, r=e=>{const b=e.getBoundingClientRect();return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),top:Math.round(b.top),bottom:Math.round(b.bottom)}};
const vis=e=>{const b=e.getBoundingClientRect();const s=getComputedStyle(e);return b.width>0&&b.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&s.opacity!=='0'};
const txt=e=>(e.innerText||e.textContent||e.getAttribute('aria-label')||'').trim().replace(/\s+/g,' ').slice(0,60);
const o={};
o.scrollWidth=document.documentElement.scrollWidth;o.innerWidth=window.innerWidth;o.overflowX=o.scrollWidth>o.innerWidth;
const hdr=document.querySelector('header')||document.querySelector('[class*=header i]');
o.headerFound=!!hdr;
if(hdr){o.headerRect=r(hdr);
 o.headerButtons=[...hdr.querySelectorAll('a,button')].filter(vis).map(e=>({tag:e.tagName,text:txt(e),href:e.getAttribute('href'),...r(e)}));
 const tel=[...hdr.querySelectorAll('a[href^="tel:"]')].filter(vis);
 const call=[...hdr.querySelectorAll('a,button')].filter(vis).filter(e=>/позвонить/i.test(txt(e)));
 o.headerTelVisible=tel.length>0||call.length>0;
 o.headerTel=[...tel,...call].map(e=>({text:txt(e),href:e.getAttribute('href'),...r(e)}));
}
const h1=document.querySelector('h1');
if(h1){const b=r(h1);o.h1={text:h1.innerText.trim().slice(0,150),...b,fullyInFirstScreen:b.top>=0&&b.bottom<=vh,fontSize:getComputedStyle(h1).fontSize,count:document.querySelectorAll('h1').length}}else o.h1=null;
const all=[...document.querySelectorAll('a,button')].filter(vis).filter(e=>{const b=e.getBoundingClientRect();return b.top<vh&&b.bottom>0});
o.cta=all.filter(e=>/обсудить|проект|заявк|связат|заказ|получить|консульт|позвон|написать|оставить|рассчитать|узнать/i.test(txt(e))).map(e=>({text:txt(e),href:e.getAttribute('href'),...r(e)})).slice(0,8);
const small=all.filter(e=>{const b=e.getBoundingClientRect();return (b.width<44||b.height<44)&&!e.closest('p,li p')});
o.smallTapCount=small.length;o.firstScreenInteractive=all.length;
o.smallTapExamples=small.slice(0,3).map(e=>({text:txt(e),href:e.getAttribute('href'),...r(e)}));
const lc=window.__lcp[window.__lcp.length-1];
if(lc){const el=lc.el;o.lcp={timeMs:Math.round(lc.t),tag:lc.tag,url:lc.url};
 if(el){o.lcp.id=el.id;o.lcp.cls=(el.className&&el.className.toString()).slice(0,80);
  if(el.tagName==='IMG'){Object.assign(o.lcp,{src:el.getAttribute('src'),currentSrc:el.currentSrc,naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,loading:el.getAttribute('loading'),fetchpriority:el.getAttribute('fetchpriority'),widthAttr:el.getAttribute('width'),heightAttr:el.getAttribute('height'),hasWH:el.hasAttribute('width')&&el.hasAttribute('height')});}
  else o.lcp.text=(el.innerText||'').slice(0,60);}}
else o.lcp=null;
const res=performance.getEntriesByType('resource');
const fonts=res.filter(e=>/\.(woff2?|ttf|otf)(\?|$)/i.test(e.name)).map(e=>({name:e.name.split('/').pop().split('?')[0],url:e.name,init:e.initiatorType,transfer:e.transferSize,encoded:e.encodedBodySize}));
o.fonts=fonts;o.fontsKB=Math.round(fonts.reduce((a,f)=>a+(f.transfer||f.encoded||0),0)/102.4)/10;
const nav=performance.getEntriesByType('navigation')[0];
o.requests=res.length+1;o.weightKB=Math.round((res.reduce((a,e)=>a+(e.transferSize||0),0)+(nav?nav.transferSize:0))/102.4)/10;
o.weightZeroTransferCount=res.filter(e=>!e.transferSize).length;
o.brokenImages=[...document.images].filter(i=>i.complete&&i.naturalWidth==0&&(i.currentSrc||i.src)).map(i=>i.currentSrc||i.src);
o.lazyUnloadedImages=[...document.images].filter(i=>!i.complete).length;
const body=document.body.innerText;
o.hasToc=/Содержание|Оглавление/i.test(body);
const anchors=[...document.querySelectorAll('a[href^="#"]')].filter(a=>a.getAttribute('href').length>1);
o.anchorLinks=anchors.length;o.anchorSamples=anchors.slice(0,5).map(a=>txt(a));
const tocEl=[...document.querySelectorAll('nav,div,aside,details')].find(e=>/^(Содержание|Оглавление)/i.test((e.innerText||'').trim())&&e.querySelectorAll('a[href^="#"]').length>1);
o.tocBlock=tocEl?{tag:tocEl.tagName,links:tocEl.querySelectorAll('a[href^="#"]').length}:null;
const time=document.querySelector('time');
o.time=time?{text:time.innerText.trim(),datetime:time.getAttribute('datetime')}:null;
o.dateInText=(body.match(/\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4}|\d{2}\.\d{2}\.\d{4}/i)||[null])[0];
o.authorEl=(document.querySelector('[rel=author],[itemprop=author],[class*=author i]')||{}).innerText||null;
o.authorInText=(body.match(/Автор[:\s][^\n]{0,60}/i)||[null])[0];
o.hasFaq=/Частые вопросы|FAQ|Вопросы и ответы/i.test(body);
const art=document.querySelector('article')||document.querySelector('main')||document.body;
const cover=art.querySelector('img');
o.coverImg=cover?{src:cover.getAttribute('src'),alt:cover.getAttribute('alt'),...r(cover)}:null;
o.iframes=[...document.querySelectorAll('iframe')].map(f=>f.src).slice(0,5);
o.mapHints=!!document.querySelector('[class*=map i],[id*=map i],ymaps,[class*=ymaps]')||o.iframes.some(s=>/map/i.test(s));
o.telLinks=[...document.querySelectorAll('a[href^="tel:"]')].map(a=>({href:a.getAttribute('href'),text:txt(a),visible:vis(a)}));
o.mailLinks=[...document.querySelectorAll('a[href^="mailto:"]')].map(a=>({href:a.getAttribute('href'),text:txt(a),visible:vis(a)}));
o.forms=[...document.forms].map(f=>({inputs:[...f.querySelectorAll('input,textarea,select')].map(i=>({type:i.type,name:i.name,placeholder:i.placeholder}))}));
o.phoneField=!!document.querySelector('input[type=tel],input[name*=phone i],input[name*=tel i],input[placeholder*=елефон i]');
return o;}"""
res=[]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    for i,u in enumerate(URLS,1):
        ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True,
          user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        ctx.add_init_script(INIT)
        ctx.route(re.compile(r"https?://[^/]*mc\.yandex\.[a-z]+/.*"),lambda r:r.abort())
        pg=ctx.new_page()
        cons=[];fails=[];bad=[]
        pg.on("console",lambda m:cons.append(m.text[:200]) if m.type=="error" else None)
        pg.on("pageerror",lambda e:cons.append("pageerror: "+str(e)[:200]))
        pg.on("requestfailed",lambda r:fails.append({"url":r.url[:150],"err":r.failure}) if "mc.yandex" not in r.url else None)
        pg.on("response",lambda r:bad.append({"url":r.url[:150],"status":r.status}) if r.status>=400 else None)
        d={"n":i,"url":u}
        try:
            resp=pg.goto(u,wait_until="load",timeout=45000)
            d["status"]=resp.status if resp else None
            try: pg.wait_for_load_state("networkidle",timeout=8000)
            except Exception: d["networkidleTimeout"]=True
            pg.wait_for_timeout(2500)
            pg.screenshot(path=f"{OUT}/shots/{i}-390.png")
            d.update(pg.evaluate(JS))
            d["consoleErrors"]=cons;d["failedRequests"]=fails;d["badResponses"]=bad
            if i in (1,2,5):
                h=pg.evaluate("document.documentElement.scrollHeight");d["pageHeight"]=h
                for y in range(0,h,600):
                    pg.evaluate(f"window.scrollTo(0,{y})");pg.wait_for_timeout(120)
                pg.evaluate("window.scrollTo(0,0)");pg.wait_for_timeout(500)
                pg.screenshot(path=f"{OUT}/shots/{i}-390-full.jpg",full_page=True,type="jpeg",quality=60)
        except Exception as e:
            d["error"]=str(e)[:300];d["consoleErrors"]=cons
        res.append(d);ctx.close();time.sleep(1.5)
    b.close()
json.dump(res,open(f"{OUT}/visual-390.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("done")
