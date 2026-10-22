import json, sys
from playwright.sync_api import sync_playwright
OUT="D:/project/tmp/task-527/"
URLS=["https://ne-prosto.ru/blog/kuda-propadayut-zayavki-iz-messendzherov","https://ne-prosto.ru/blog/besplatnye-kirillicheskie-shrifty","https://ne-prosto.ru/blog/upakovka-kotoraya-prodaet-priemy","https://ne-prosto.ru/uslugi/ii-assistent-dlya-biznesa"]
JS=r"""()=>{const w=document.querySelector('.article-wrapper');const t=document.querySelector('.np-toc');const h=document.querySelector('h1');const c=document.querySelector('.article-content');
const r=e=>e?(b=>({l:Math.round(b.left),r:Math.round(b.right),w:Math.round(b.width)}))(e.getBoundingClientRect()):null;
return {vw:innerWidth,sw:document.documentElement.scrollWidth,css:[...document.querySelectorAll('link[href*=article]')].map(l=>l.getAttribute('href')),
jc:w?getComputedStyle(w).justifyContent:null,h1:r(h),content:r(c),toc:r(t),h1n:document.querySelectorAll('h1').length,footer:!!document.querySelector('footer'),
img:r(document.querySelector('.article__img'))}}"""
res={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for u in URLS[:1]+[None]:
        pass
    for vw,vh,mob in [(1920,1080,False),(1440,900,False),(1366,768,False),(390,844,True)]:
        ctx=b.new_context(viewport={"width":vw,"height":vh},is_mobile=mob,device_scale_factor=1)
        pg=ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        for u in URLS:
            r=pg.goto(u,wait_until="networkidle")
            d=pg.evaluate(JS); d["status"]=r.status; d["errs"]=errs[:]
            res[f"{vw} {u.split('/')[-1]}"]=d
            if "kuda" in u: pg.screenshot(path=f"{OUT}after-{vw}.png")
        ctx.close()
    b.close()
for k,v in res.items(): print(k, json.dumps(v,ensure_ascii=False))
