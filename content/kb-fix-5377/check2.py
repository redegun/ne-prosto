import re, time, urllib.request, json
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(u):
    try:
        r = op.open(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 task5377-check'}), timeout=30); return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8', 'replace')
out = {}
for p in ['/404', '/net-takoj-stranicy-5377b', '/kompaniya/', '/kompaniya/v-rolyax/', '/portfolio/presentation-anglomania', '/portfolio/presentation-parket', '/portfolio/presentation-sadodel', '/portfolio/presentation-servisok', '/portfolio/presentation-stdfast', '/portfolio/presentation-trump', '/portfolio/internet-magazin-topwaters', '/']:
    st, h = get('https://ne-prosto.ru' + p)
    main = h.split('id="np-main"', 1)[-1].split('<footer', 1)[0]
    imgs = re.findall(r'<img\b[^>]*>', main)
    pres = [i for i in imgs if 'presentation/' in i]
    r = {'status': st, 'robots': re.findall(r'<meta name="robots" content="([^"]*)"', h), 'h1': len(re.findall(r'<h1\b', h)),
         'typo': [w for w in ['Графическая дизайнер', 'Пвл Мельник'] if w in h], 'pavel': 'Павел Мельник' in h,
         'gallery_imgs': len(pres), 'gallery_empty_alt': [re.search(r'src="([^"]+)"', i).group(1).split('/')[-1] for i in pres if 'alt=""' in i],
         'gallery_alts_sample': [re.search(r'alt="([^"]*)"', i).group(1) for i in pres if 'alt=""' not in i][:2], 'unparsed': len(re.findall(r'\[\[', h))}
    out[p] = r; print(p, json.dumps(r, ensure_ascii=False)); time.sleep(1)
json.dump(out, open('check2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
