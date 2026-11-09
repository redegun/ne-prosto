import sys, json
from playwright.sync_api import sync_playwright
tag = sys.argv[1]
URLS = ["https://ne-prosto.ru/portfolio/merci", "https://ne-prosto.ru/portfolio/kppf", "https://ne-prosto.ru/portfolio/", "https://ne-prosto.ru/", "https://ne-prosto.ru/portfolio/vinyl-tm"]
CLS = "window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"
res = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    for w, h in ((1440, 900), (390, 844)):
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=(w == 390))
        for u in URLS:
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.add_init_script(CLS)
            r = pg.goto(u + ("" if "?" in u else "?nocache=1882"), wait_until="networkidle", timeout=90000)
            pg.wait_for_timeout(2500)
            for y in range(0, 20000, 700):
                pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(60)
            pg.wait_for_timeout(800)
            d = pg.evaluate("""()=>({cls:window.__cls,h1:document.querySelectorAll('h1').length,
              ov:document.documentElement.scrollWidth-window.innerWidth,
              did:document.querySelectorAll('.np-did__item').length, card:document.querySelectorAll('.np-did-card').length,
              footer:!!document.querySelector('footer')})""")
            d.update(url=u, w=w, code=r.status, errs=errs[:3])
            slug = u.rstrip('/').split('/')[-1] or 'home'
            if tag == "after" and slug in ("merci", "kppf", "portfolio"):
                pg.evaluate("window.scrollTo(0,0)")
                el = pg.query_selector(".np-did") if slug != "portfolio" else pg.query_selector("a[href='/portfolio/merci']")
                if el:
                    if slug != "portfolio":
                        pg.evaluate("document.querySelectorAll('.np-did__item')[0].open=true")
                        pg.wait_for_timeout(800)
                    el.scroll_into_view_if_needed(); pg.wait_for_timeout(1500)
                    if slug == "portfolio":
                        pg.evaluate("document.querySelector(\"a[href='/portfolio/merci']\").closest('article').scrollIntoView()")
                        pg.wait_for_timeout(1500)
                        pg.screenshot(path=f"shots/{tag}-{slug}-{w}.png")
                    else:
                        pg.evaluate("document.querySelector('.np-did').scrollIntoView()"); pg.wait_for_timeout(1200); pg.screenshot(path=f"shots/{tag}-{slug}-{w}.png")
            res.append(d); print(json.dumps(d, ensure_ascii=False)); pg.close()
        ctx.close()
    b.close()
json.dump(res, open(f"qa-{tag}.json", "w"), ensure_ascii=False, indent=1)
