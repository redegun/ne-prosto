from playwright.sync_api import sync_playwright
URL="https://ne-prosto.ru/blog/kuda-propadayut-zayavki-iz-messendzherov"
V={"now":"","A":".article-wrapper{justify-content:center!important}","B":".article-wrapper{justify-content:space-between!important}"}
with sync_playwright() as pw:
    br=pw.chromium.launch()
    for w,h in [(1920,1080),(1440,900)]:
        for k,css in V.items():
            pg=br.new_page(viewport={"width":w,"height":h}); pg.goto(URL,wait_until="networkidle")
            if css: pg.add_style_tag(content=css)
            pg.evaluate("document.querySelector('.np-toc').scrollIntoView({block:'start'});scrollBy(0,-140)"); pg.wait_for_timeout(700)
            r=pg.evaluate("(()=>{const b=document.querySelector('.np-toc').getBoundingClientRect(),c=document.querySelector('.article-content').getBoundingClientRect();return [Math.round(c.left),Math.round(b.right),innerWidth-Math.round(b.right)]})()")
            print(w,k,"text-left,toc-right,right-gap",r)
            pg.screenshot(path=f"{k}-{w}.png"); pg.close()
    br.close()
