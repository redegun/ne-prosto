import json
from playwright.sync_api import sync_playwright
URL="https://ne-prosto.ru/blog/kuda-propadayut-zayavki-iz-messendzherov"
JS=r"""()=>{const w=document.querySelector('.article-wrapper');const cs=getComputedStyle(w);
return {vw:innerWidth,gap:cs.columnGap,jc:cs.justifyContent,kids:[...w.children].map(e=>{const b=e.getBoundingClientRect();return {t:e.tagName,c:e.className.toString().slice(0,40),l:Math.round(b.left),r:Math.round(b.right),gc:getComputedStyle(e).gridColumn}})}}"""
with sync_playwright() as pw:
    br=pw.chromium.launch()
    for w in (1920,1600,1440,1366,1280,1100):
        pg=br.new_page(viewport={"width":w,"height":900}); pg.goto(URL,wait_until="networkidle")
        print(json.dumps(pg.evaluate(JS),ensure_ascii=False)); pg.close()
    br.close()
