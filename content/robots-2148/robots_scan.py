"""task 2148: meta robots на всех опубликованных HTML-страницах ne-prosto (по списку из probe2.out)."""
import json, re, sys, urllib.request, ssl
from pathlib import Path

out = sys.argv[1]
uris = []
sec = False
for line in Path('probe2.out').read_text(encoding='utf-8').splitlines():
    if line.startswith('===== all published'):
        sec = True; continue
    if sec and '\t' in line:
        rid, uri, tpl, ct, cls = line.split('\t')
        if ct == '1':
            uris.append((int(rid), uri, int(tpl)))
res = {}
ctx = ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))
for rid, uri, tpl in uris:
    url = 'https://ne-prosto.ru/' + ('' if uri == 'index' else uri)
    try:
        r = opener.open(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 np-task2148'}), timeout=30)
        code, html = r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        code, html = e.code, e.read().decode('utf-8', 'replace')
    except Exception as e:
        code, html = str(e), ''
    head = html.split('</head>')[0]
    robots = re.findall(r'<meta[^>]+name=["\']robots["\'][^>]*>', head, re.I)
    res[url] = {'id': rid, 'tpl': tpl, 'code': code, 'robots': robots,
                'h1': len(re.findall(r'<h1[\s>]', html, re.I)), 'len': len(html),
                'head_end': html.count('</head>')}
    print(code, rid, tpl, url, robots, flush=True)
Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
