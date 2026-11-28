import asyncio, sys, pathlib
from playwright.async_api import async_playwright
from PIL import Image
d = pathlib.Path(sys.argv[1]); svg = (d/'favicon.svg').read_text()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        for s in (16, 32, 48, 180, 192):
            await pg.set_viewport_size({'width': s, 'height': s})
            await pg.set_content(f'<html><body style="margin:0;background:transparent">{svg.replace("<svg ", f"<svg width=\"{s}\" height=\"{s}\" ")}</body></html>')
            await pg.screenshot(path=str(d/f'p{s}.png'), omit_background=True)
        await b.close()
asyncio.run(main())
im = Image.open(d/'p48.png').convert('RGBA')
im.save(d/'favicon.ico', sizes=[(16,16),(32,32),(48,48)])
Image.open(d/'p180.png').convert('RGBA').save(d/'apple-touch-icon.png', optimize=True)
Image.open(d/'p192.png').convert('RGBA').save(d/'favicon-192.png', optimize=True)
print('ok')
