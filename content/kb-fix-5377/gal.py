import json, time, urllib.request, pathlib, io
from PIL import Image, ImageDraw
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
d = [x for x in json.load(open('imgs.json', encoding='utf-8')) if 'src' in x and not x['src'].endswith('.svg')]
seen = {}; thumbs = []
for x in d:
    src = x['src']
    if src not in seen:
        b = op.open('https://ne-prosto.ru/' + src.lstrip('/'), timeout=60).read(); time.sleep(0.3)
        im = Image.open(io.BytesIO(b)).convert('RGB'); im.thumbnail((260, 520)); seen[src] = im
    thumbs.append((f"{x['id']}#{x['i']} {src.split('/')[-1]}", seen[src]))
for k in range(0, len(thumbs), 20):
    part = thumbs[k:k+20]; W = 5*270; H = 4*545
    sheet = Image.new('RGB', (W, H), 'white'); dr = ImageDraw.Draw(sheet)
    for j, (lab, im) in enumerate(part):
        x0 = (j % 5)*270; y0 = (j//5)*545
        sheet.paste(im, (x0+5, y0+20)); dr.text((x0+5, y0+3), lab, fill='red')
    sheet.save(f'gal/sheet{k//20}.jpg', quality=80)
print(len(thumbs))
