import json,re
from playwright.sync_api import sync_playwright
JS=r"""()=>{const o={};const h=document.querySelector('h1');
o.imgs=[...document.querySelectorAll('img')].slice(0,6).map(i=>({src:(i.getAttribute('src')||'').slice(-60),alt:i.getAttribute('alt'),cls:i.className,top:Math.round(i.getBoundingClientRect().top+scrollY),inArticle:!!i.closest('article')}));
o.articleImg=(document.querySelector('.article__img')||{}).alt;
const top=document.body.innerText.slice(0,900);o.topText=top;
const i=document.body.innerText.search(/Содержание|Оглавление/i);o.tocCtx=document.body.innerText.slice(i,i+300);
o.h1parent=h?h.parentElement.innerText.slice(0,300):null;
o.ldjson=[...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>s.textContent.slice(0,400));
o.faqHeads=[...document.querySelectorAll('h2,h3')].map(e=>e.innerText.trim().slice(0,70));
return o}"""
with sync_playwright() as p:
    b=p.chromium.launch(headless=True);out={}
    for u in ["https://ne-prosto.ru/blog/semanticheskoe-yadro-sajta","https://ne-prosto.ru/blog/besplatnye-kirillicheskie-shrifty"]:
        c=b.new_context(viewport={"width":390,"height":844},is_mobile=True);c.route(re.compile(r".*mc\.yandex\..*"),lambda r:r.abort())
        pg=c.new_page();pg.goto(u,wait_until="load");pg.wait_for_timeout(2500);out[u]=pg.evaluate(JS);c.close()
    json.dump(out,open("evidence/article-check.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
    for u,o in out.items():
        print(u);print(o['imgs']);print(o['articleImg']);print(repr(o['topText'][:500]));print(repr(o['tocCtx']));print(o['faqHeads']);print(o['ldjson'][:2])
