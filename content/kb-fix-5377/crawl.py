import re, time, json, urllib.request, ssl, sys
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(u):
    try:
        r = op.open(urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0 task5377-check'}), timeout=30); return r.status, r.read().decode('utf-8','replace'), r.geturl()
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8','replace'), u
s, sm, _ = get('https://ne-prosto.ru/sitemap.xml')
locs = re.findall(r'<loc>([^<]+)</loc>', sm)
extra = ['https://ne-prosto.ru/index.php','https://ne-prosto.ru/KOORDINATYI','https://ne-prosto.ru/uslugi/sajtyi?utm_source=test','https://ne-prosto.ru/blog/?page=2','https://ne-prosto.ru/404','https://ne-prosto.ru/net-takoj-stranicy-5377','https://ne-prosto.ru/politika-konfidencialnosti']
res = {'sitemap_count': len(locs), 'home_in_sitemap': 'https://ne-prosto.ru/' in locs, 'sitemap_has': {k: any(k in l for l in locs) for k in ['/404','index-new','page-style','sitemap.xml','v-rolyax/<','politika']}, 'pages': []}
for u in locs + extra:
    st, h, fu = get(u)
    can = re.findall(r'<link rel="canonical" href="([^"]*)"', h)
    rob = re.findall(r'<meta name="robots" content="([^"]*)"', h)
    icons = len(re.findall(r'rel="(?:icon|apple-touch-icon)"', h))
    imgs = re.findall(r'<img\b[^>]*>', h)
    cover = [i for i in imgs if 'article__img' in i]
    cards = [i for i in imgs if 'phpthumbof/cache' in i or 'design-20261018/services/' in i]
    empty_cards = [i for i in cards if re.search(r"alt=(\"\"|'')", i)]
    res['pages'].append({'url': u, 'status': st, 'canonical': can, 'robots': rob, 'icons': icons, 'h1': len(re.findall(r'<h1\b', h)), 'cover_alt': [re.search(r"alt=[\"']([^\"']*)", i).group(1) for i in cover], 'cards': len(cards), 'cards_empty_alt': len(empty_cards), 'unparsed': len(re.findall(r'\[\[|\{\$_pls', h)), 'len': len(h)})
    time.sleep(1.0)
json.dump(res, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
p = res['pages']
print('sitemap', res['sitemap_count'], 'home', res['home_in_sitemap'], res['sitemap_has'])
print('status', {s: sum(1 for x in p if x['status']==s) for s in set(x['status'] for x in p)})
bad = [x for x in p if x['status']==200 and (len(x['canonical'])!=1 or x['icons']!=4 or x['h1']!=1 or x['unparsed'])]
for x in bad: print('BAD', x['url'], x['status'], x['canonical'], x['icons'], x['h1'], x['unparsed'])
mis = [x for x in p if x['status']==200 and x['canonical'] and x['canonical'][0].rstrip('/') != x['url'].split('?')[0].rstrip('/')]
for x in mis: print('CAN!=URL', x['url'], '->', x['canonical'][0])
print('cards empty alt total', sum(x['cards_empty_alt'] for x in p), 'cards', sum(x['cards'] for x in p))
print('covers empty', [x['url'] for x in p if x['cover_alt'] and not all(x['cover_alt'])])
for x in p:
    if x['robots'] and 'noindex' in x['robots'][0]: print('NOINDEX', x['url'], x['status'])
