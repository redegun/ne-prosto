"""#541: макеты 3 вариантов оформления CTA-блоков на живой статье (CSS вставляется только в браузер)."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

URL = "https://ne-prosto.ru/blog/kuda-propadayut-zayavki-iz-messendzherov"
OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# общий сброс: кнопка залитая, без «прозрачного» вида
BTN = """
.np-cta .np-cta__button{border:0!important;font-weight:600!important;min-height:52px!important;padding:13px 22px!important}
.np-cta .np-cta__button::after{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;font-size:20px!important}
"""

# 1) мягкая подложка со скруглением + залитая тёмная кнопка (основная кнопка сайта) с лаймовым «+»
SOFT = """
.np-cta{background:#e9ebe4!important;border:0!important;border-radius:16px!important;padding:34px 38px 36px!important}
.np-cta .np-cta__text{color:#45483f!important}
.np-cta .np-cta__kicker{color:#45483f!important}
.np-cta .np-cta__button{background:#191b18!important;color:#f6f6f1!important;border-radius:10px!important}
.np-cta .np-cta__button::after{background:#e9f77c;color:#191b18}
@media(max-width:700px){.np-cta{padding:24px 20px 24px!important;border-radius:14px!important}}
"""

# 2) линия слева фирменным оливковым + залитая лаймовая кнопка с тёмным текстом
LINE = """
.np-cta{background:transparent!important;border:0!important;border-left:4px solid #6a7824!important;border-radius:0!important;padding:6px 0 8px 30px!important}
.np-cta .np-cta__kicker{color:#5b6720!important;font-weight:600}
.np-cta .np-cta__text{color:#45483f!important}
.np-cta .np-cta__button{background:#e9f77c!important;color:#191b18!important;border:1px solid #191b18!important;border-radius:8px!important}
.np-cta .np-cta__button::after{background:#191b18;color:#e9f77c}
@media(max-width:700px){.np-cta{padding:4px 0 6px 18px!important}}
"""

# 3) средний мягкий (как 1), нижний по услуге — тёмный блок цвета подвала + лаймовая кнопка
DARK = SOFT + """
.np-cta--end{background:#191b18!important;color:#f6f6f1!important}
.np-cta--end .np-cta__title{color:#f6f6f1!important}
.np-cta--end .np-cta__text{color:#c9ccc2!important}
.np-cta--end .np-cta__kicker{color:#e9f77c!important}
.np-cta--end .np-cta__link{color:#e9f77c!important}
.np-cta--end .np-cta__button{background:#e9f77c!important;color:#191b18!important}
.np-cta--end .np-cta__button::after{background:#191b18;color:#e9f77c}
"""

VARIANTS = [("0", "Сейчас", ""), ("1", "Вариант 1 — мягкая подложка", BTN + SOFT),
            ("2", "Вариант 2 — линия слева", BTN + LINE), ("3", "Вариант 3 — тёмный нижний блок", BTN + DARK)]
VIEWS = [("desktop", 1440, 900, 1), ("mobile", 390, 844, 3)]


def crop_blocks(page, scale):
    """Обрезки вокруг среднего и нижнего блока с кусочком текста статьи сверху и снизу."""
    page.add_style_tag(content=".np-header,header{position:static!important}")
    shots = []
    for sel in (".np-cta--mid", ".np-cta--end"):
        el = page.locator(sel)
        el.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        b = page.evaluate("""s=>{const r=document.querySelector(s).getBoundingClientRect();
            return {y:r.top+scrollY,h:r.height}}""", sel)
        vw = page.viewport_size["width"]
        pad = 170 if vw > 500 else 130
        shots.append(page.screenshot(full_page=True, clip={"x": 0, "y": max(0, b["y"] - pad), "width": vw,
                                                           "height": b["h"] + 2 * pad}))
    return shots


def main():
    from io import BytesIO
    with sync_playwright() as p:
        br = p.chromium.launch()
        for vname, w, h, scale in VIEWS:
            for key, title, css in VARIANTS:
                ctx = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=scale,
                                     is_mobile=vname == "mobile", has_touch=vname == "mobile")
                page = ctx.new_page()
                page.goto(URL, wait_until="networkidle")
                if css:
                    page.add_style_tag(content=css)
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(500)
                imgs = [Image.open(BytesIO(s)) for s in crop_blocks(page, scale)]
                gap = 40 * scale
                head = 70 * scale
                W = imgs[0].width
                H = head + sum(i.height for i in imgs) + gap
                sheet = Image.new("RGB", (W, H), "#ffffff")
                d = ImageDraw.Draw(sheet)
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26 * scale if vname == "desktop" else 13 * scale)
                d.text((24 * scale, 20 * scale), title + (" · монитор" if vname == "desktop" else " · телефон"),
                        fill="#191b18", font=font)
                y = head
                for n, im in enumerate(imgs):
                    sheet.paste(im, (0, y))
                    y += im.height
                    if n == 0:
                        d.rectangle([0, y, W, y + gap], fill="#cfd2c8")
                        sf = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14 * scale)
                        d.text((24 * scale, y + 10 * scale), "… дальше статья …", fill="#45483f", font=sf)
                        y += gap
                if vname == "mobile":
                    sheet = sheet.resize((sheet.width * 2 // 3, sheet.height * 2 // 3), Image.LANCZOS)
                sheet.save(OUT / f"v{key}-{vname}.png", optimize=True)
                ctx.close()
        br.close()


if __name__ == "__main__":
    main()
