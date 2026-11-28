#!/usr/bin/env python3
"""Аккуратный обход ne-prosto.ru для аудита #5182: только GET, пауза 1.1 с, без форм и POST.
Главная + все URL sitemap.xml + проверки зеркал/служебных путей. HTML → crawl/html/, сводка → crawl/crawl.json."""
import json, os, re, sys, time, hashlib
import requests

BASE = "https://ne-prosto.ru"
UA = "Mozilla/5.0 (compatible; StudioQA/1.0; +ne-prosto)"
OUT = sys.argv[1] if len(sys.argv) > 1 else "D:/project/tmp/task-5182/crawl"
os.makedirs(OUT + "/html", exist_ok=True)
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "ru,en;q=0.8", "Accept-Encoding": "gzip, deflate"})
S.trust_env = False

sm = open(OUT + "/sitemap.xml", encoding="utf-8").read()
locs = re.findall(r"<loc>([^<]+)</loc>", sm)


def kind(u):
    p = u.replace(BASE, "")
    if p in ("", "/"):
        return "home"
    if p.startswith("/blog/") and p != "/blog/":
        return "article"
    if p == "/blog/":
        return "blog"
    if p == "/uslugi/":
        return "hub"
    if p.startswith("/uslugi/") or p.startswith("/podderzhka/"):
        return "service"
    if p == "/portfolio/":
        return "portfolio"
    if p.startswith("/portfolio/"):
        return "case"
    if p.startswith("/kompaniya/v-rolyax/"):
        return "person"
    if p.startswith("/kompaniya/klientyi/") and p != "/kompaniya/klientyi/":
        return "client"
    if p.startswith("/kompaniya/vakansii/") and p != "/kompaniya/vakansii/":
        return "vacancy"
    if p == "/koordinatyi":
        return "contacts"
    return "page"


PAGES = [("home", BASE + "/")] + [(kind(u), u) for u in locs]
EXTRA = ["/politika-konfidencialnosti", "/soglasie-na-obrabotku-personalnyh-dannyh", "/index-new", "/404",
         "/kompaniya/komanda", "/blog/?page=2"]
PAGES += [("extra", BASE + p) for p in EXTRA]

CHECKS = [
    ("http_root", "http://ne-prosto.ru/"),
    ("www_root", "https://www.ne-prosto.ru/"),
    ("http_www", "http://www.ne-prosto.ru/koordinatyi"),
    ("index_php", BASE + "/index.php"),
    ("index_php_id", BASE + "/index.php?id=1"),
    ("index_html", BASE + "/index.html"),
    ("noslash_hub", BASE + "/uslugi"),
    ("slash_leaf", BASE + "/koordinatyi/"),
    ("slash_article", BASE + "/blog/etapy-razrabotki-sajta/"),
    ("upper", BASE + "/KOORDINATYI"),
    ("double_slash", BASE + "//uslugi/sajtyi"),
    ("utm", BASE + "/uslugi/sajtyi?utm_source=test"),
    ("ymclid", BASE + "/?yclid=123"),
    ("rnd404", BASE + "/net-takoj-stranicy-5182"),
    ("rnd404_blog", BASE + "/blog/net-takoj-stati-5182"),
    ("rnd404_svc", BASE + "/uslugi/net-takoj-uslugi-5182"),
    ("favicon", BASE + "/favicon.ico"),
    ("apple_touch", BASE + "/apple-touch-icon.png"),
    ("core", BASE + "/core/config/config.inc.php"),
    ("core_dir", BASE + "/core/"),
    ("manager", BASE + "/manager/"),
    ("connectors", BASE + "/connectors/"),
    ("setup", BASE + "/setup/"),
    ("autopilot", BASE + "/_autopilot/np-publish.php"),
    ("agent_tmp", BASE + "/_agent_tmp/"),
    ("p_dir", BASE + "/p/"),
    ("llms", BASE + "/llms.txt"),
    ("sitemap_gz", BASE + "/sitemap.xml.gz"),
    ("robots_http", "http://ne-prosto.ru/robots.txt"),
    ("robots_www", "https://www.ne-prosto.ru/robots.txt"),
    ("git", BASE + "/.git/config"),
    ("env", BASE + "/.env"),
    ("phpinfo", BASE + "/phpinfo.php"),
    ("feed", BASE + "/blog/rss"),
    ("feed2", BASE + "/rss.xml"),
]


def save(path, text):
    name = re.sub(r"[^a-zA-Z0-9]+", "_", path.replace(BASE, "").strip("/")) or "home"
    if len(name) > 120:
        name = name[:100] + "_" + hashlib.md5(name.encode()).hexdigest()[:8]
    fn = f"{OUT}/html/{name}.html"
    with open(fn, "w", encoding="utf-8") as f:
        f.write(text)
    return os.path.basename(fn)


HDR = ["server", "content-type", "cache-control", "x-robots-tag", "vary", "content-encoding", "link", "last-modified",
       "expires", "x-powered-by", "strict-transport-security", "x-frame-options", "content-security-policy",
       "x-content-type-options", "referrer-policy", "permissions-policy", "location", "set-cookie", "etag"]


def hsub(h):
    return {k: h.get(k) for k in HDR if h.get(k) is not None}


res = {"pages": [], "checks": [], "started": time.strftime("%Y-%m-%d %H:%M:%S")}
n = 0
for kd, url in PAGES:
    t0 = time.time()
    try:
        r = S.get(url, allow_redirects=False, timeout=30)
        el = round(time.time() - t0, 3)
        rec = {"kind": kd, "url": url, "status": r.status_code, "time": el, "headers": hsub(r.headers),
               "bytes": len(r.content), "http_version": r.raw.version}
        if r.status_code in (301, 302, 307, 308):
            rec["location"] = r.headers.get("location")
        if "html" in (r.headers.get("content-type") or ""):
            r.encoding = "utf-8"
            rec["file"] = save(url, r.text)
    except Exception as e:
        rec = {"kind": kd, "url": url, "error": str(e)}
    res["pages"].append(rec)
    n += 1
    print(n, rec.get("status"), rec.get("time"), url, flush=True)
    time.sleep(1.1)

for label, url in CHECKS:
    t0 = time.time()
    try:
        r = S.get(url, allow_redirects=False, timeout=30)
        rec = {"label": label, "url": url, "status": r.status_code, "time": round(time.time() - t0, 3),
               "headers": hsub(r.headers), "bytes": len(r.content), "location": r.headers.get("location")}
        ct = r.headers.get("content-type") or ""
        if label in ("favicon", "apple_touch"):
            rec["head_bytes_hex"] = r.content[:16].hex()
        if "text" in ct or "html" in ct or "json" in ct or "xml" in ct:
            r.encoding = r.encoding or "utf-8"
            rec["body_head"] = r.text[:300]
            if "html" in ct and (label.startswith("rnd404") or label in ("p_dir", "utm", "upper")):
                rec["file"] = save("check_" + label, r.text)
    except Exception as e:
        rec = {"label": label, "url": url, "error": str(e)}
    res["checks"].append(rec)
    n += 1
    print(n, label, rec.get("status"), rec.get("location"), flush=True)
    time.sleep(1.1)

res["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
json.dump(res, open(OUT + "/crawl.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("done", n)
