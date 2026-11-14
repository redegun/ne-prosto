"""task 2452: обход всех URL из sitemap ne-prosto.ru — код, H1, </head>, счётчик Метрики. usage: scan.py out.json"""
import json, re, sys, urllib.request, concurrent.futures as cf

UA = {"User-Agent": "Mozilla/5.0 (task2452 scan)"}
NOPROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def get(u):
    try:
        r = NOPROXY.open(urllib.request.Request(u, headers=UA), timeout=40)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa
        return 0, str(e)


code, sm = get("https://ne-prosto.ru/sitemap.xml")
urls = sorted(set(re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm)))
extra = ["https://ne-prosto.ru/", "https://ne-prosto.ru/kompaniya/vakansii/", "https://ne-prosto.ru/politika-konfidencialnosti"]
urls = sorted(set(urls + extra))


def one(u):
    c, h = get(u)
    return u, {
        "code": c,
        "h1": len(re.findall(r"<h1[\s>]", h, re.I)),
        "head_close": h.count("</head>"),
        "init": h.count('ym(27066311,"init"'),
        "goal": h.count("document.onaf_complete"),
        "tagjs": h.count("mc.yandex.ru/metrika/tag.js?id=27066311"),
        "forms": len(re.findall(r"<form[\s>]", h, re.I)),
        "len": len(h),
        "footer": h.count("np-footer__legal"),
        "mod_tags": h.count("[["),
    }


with cf.ThreadPoolExecutor(4) as ex:
    res = dict(ex.map(one, urls))
json.dump(res, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
bad = {u: r for u, r in res.items() if r["code"] != 200}
print(f"sitemap {code}, urls {len(res)}, non-200 {len(bad)}, with init {sum(1 for r in res.values() if r['init'] == 1)}, init!=1 {[u for u, r in res.items() if r['code'] == 200 and r['init'] != 1][:10]}")
