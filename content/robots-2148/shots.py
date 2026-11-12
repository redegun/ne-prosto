"""task 2148: live-QA 1440/390 — главная, статья, блог: скрин, overflow, битые картинки, ошибки JS, meta robots из DOM."""
import json, sys
from playwright.sync_api import sync_playwright

URLS = ["https://ne-prosto.ru/", "https://ne-prosto.ru/blog/skorost-zagruzki-sajta", "https://ne-prosto.ru/blog/", "https://ne-prosto.ru/kompaniya/vakansii/"]
res = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", args=["--no-proxy-server"])
    for w, h in [(1440, 900), (390, 844)]:
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
        for u in URLS:
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            r = pg.goto(u, wait_until="networkidle", timeout=60000)
            pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(1500); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
            d = pg.evaluate("""() => ({sw: document.documentElement.scrollWidth, iw: innerWidth,
                h1: document.querySelectorAll('h1').length,
                header: !!document.querySelector('header'), footer: !!document.querySelector('footer'),
                broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.src).map(i => i.src),
                robots: [...document.querySelectorAll('meta[name=robots]')].map(m => m.content)})""")
            name = f"shots/{w}-{u.rstrip('/').split('/')[-1] or 'home'}.png"
            pg.screenshot(path=name, full_page=False)
            res.append({"w": w, "url": u, "code": r.status, "errs": errs, **d, "shot": name})
            print(w, r.status, u, d, errs, flush=True)
            pg.close()
        ctx.close()
    b.close()
json.dump(res, open("qa.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
