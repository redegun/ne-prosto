# task 529: проверка, что оглавление не заезжает на «Ещё интересное». usage: check.py [local] [prefix]
import sys, json
from playwright.sync_api import sync_playwright
LOCAL = len(sys.argv)>1 and sys.argv[1]=='local'
PFX = sys.argv[2] if len(sys.argv)>2 else 'x'
BASE='https://ne-prosto.ru/blog/'
ARTS=['kuda-propadayut-zayavki-iz-messendzherov','besplatnye-kirillicheskie-shrifty','upakovka-kotoraya-prodaet-priemy','priznaki-chto-pora-na-rebrending','servisy-dlya-podbora-cveta','kakie-stranicy-pomogayut-poluchat-obrashcheniya','gde-brat-foto-i-illyustracii-stoki','instrumenty-dlya-firmennogo-stilya']
SIZES=[(1920,1080),(1440,900),(1366,768),(390,844)]
JS="""()=>{const t=document.querySelector('.np-toc'),s=document.querySelector('.article-similar'),c=document.querySelector('.article-content');
if(!c)return {content:false,body:document.body.className};if(!t)return {toc:false,len:c.offsetHeight};const H=innerHeight,res={toc:true,len:c.offsetHeight,overlap:0,stickyOk:null,hscroll:document.documentElement.scrollWidth>innerWidth};
const end=document.documentElement.scrollHeight;let maxOv=-1e9,stuck=false;
for(let y=0;y<end;y+=150){scrollTo(0,y);const tr=t.getBoundingClientRect(),sr=s?s.getBoundingClientRect():{top:1e9},cr=c.getBoundingClientRect();
 if(innerWidth>1100){const ov=tr.bottom-sr.top;if(ov>maxOv)maxOv=ov; if(Math.abs(tr.top-32)<2 && cr.top<0) stuck=true; if(tr.bottom-cr.bottom>maxOv&&false){} res.tocVsText=Math.max(res.tocVsText||-1e9,tr.bottom-cr.bottom);}}
res.maxOverlapPx=Math.round(maxOv);res.stuckWhileReading=stuck;res.tocVsText=Math.round(res.tocVsText||0);return res}"""
out=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in SIZES:
        ctx=b.new_context(viewport={'width':w,'height':h}, is_mobile=(w<500), has_touch=(w<500))
        if LOCAL:
            ctx.route('**/design-20261018/article.css*', lambda r: r.fulfill(path='article.css', content_type='text/css'))
            ctx.route('**/design-20261018/article.js*', lambda r: r.fulfill(path='article.js', content_type='application/javascript'))
        pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        for a in ARTS:
            resp=pg.goto(BASE+a, wait_until='networkidle')
            r=pg.evaluate(JS); r.update(art=a,w=w,code=resp.status,errs=len(errs)); out.append(r)
            if a in ('kuda-propadayut-zayavki-iz-messendzherov','servisy-dlya-podbora-cveta'):
                if w>1100:
                    pg.evaluate("()=>{const s=document.querySelector('.article-similar');scrollTo(0,s.getBoundingClientRect().top+scrollY-innerHeight*0.3)}")
                else:
                    pg.evaluate("()=>scrollTo(0,0)")
                pg.wait_for_timeout(300); pg.screenshot(path=f'{PFX}-{w}-{a[:12]}.png')
        ctx.close()
    b.close()
for r in out: print(json.dumps(r,ensure_ascii=False))
