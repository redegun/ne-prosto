#!/usr/bin/env python3
"""Доп. проверки ne-prosto.ru (#5182): категории, боты, вес картинок и CSS шрифтов. GET/HEAD, пауза 1.5 с."""
import json, re, time, requests
B = "https://ne-prosto.ru"
UA = "Mozilla/5.0 (compatible; StudioQA/1.0; +ne-prosto)"
OUT = "D:/project/tmp/task-5182/crawl"
S = requests.Session(); S.trust_env = False; S.headers.update({"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
res = {"pages": [], "bots": [], "assets": []}
for p in ["/blog/blog-category/news/", "/blog/blog-category/brending/", "/portfolio/portfolio-category/sites/", "/index.php"]:
    r = S.get(B + p, allow_redirects=False, timeout=30)
    rec = {"url": B + p, "status": r.status_code, "location": r.headers.get("location"), "bytes": len(r.content)}
    if r.status_code == 200:
        r.encoding = "utf-8"; t = r.text
        name = re.sub(r"[^a-zA-Z0-9]+", "_", p.strip("/")) or "x"
        open(OUT + "/html/c2_" + name + ".html", "w", encoding="utf-8").write(t)
        m = re.search(r"<title>([^<]*)", t); rec["title"] = m.group(1).strip() if m else None
        rec["canonical"] = re.findall(r'<link[^>]+rel="canonical"[^>]*>', t)
        m = re.search(r'<meta name="robots" content="([^"]+)"', t); rec["robots"] = m.group(1) if m else None
        m = re.search(r'<meta name="description" content="([^"]*)"', t); rec["description"] = m.group(1) if m else None
        rec["h1"] = re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)[:2]
        rec["cards"] = len(set(re.findall(r'href="([^"]*(?:blog|portfolio)/[a-z0-9-]+)"', t)))
    res["pages"].append(rec); print(rec["status"], p, rec.get("title"), flush=True); time.sleep(1.5)
BOTS = {"Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "YandexBot": "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
        "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
        "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
        "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"}
for name, ua in BOTS.items():
    r = requests.get(B + "/blog/semanticheskoe-yadro-sajta", headers={"User-Agent": ua}, timeout=30, allow_redirects=False, proxies={"http": None, "https": None})
    rec = {"bot": name, "status": r.status_code, "bytes": len(r.content), "has_h1": "<h1" in r.text}
    res["bots"].append(rec); print(rec, flush=True); time.sleep(1.5)
ASSETS = ["/images/portfolio/stankin/photo-31.jpg",
          "/assets/neprosto/design-20261018/site.css?v=11",
          "/assets/components/minifyx/cache/styles_8d58812fbf.css",
          "/images/godnota/blog/semanticheskoe-yadro-sajta.jpg"]
for a in ASSETS:
    r = S.get(B + a, timeout=30)
    rec = {"url": B + a, "status": r.status_code, "bytes": len(r.content), "ctype": r.headers.get("content-type"),
           "enc": r.headers.get("content-encoding"), "cache": r.headers.get("cache-control")}
    if "css" in (r.headers.get("content-type") or ""):
        r.encoding = "utf-8"; css = r.text
        rec["font_urls"] = sorted(set(re.findall(r"url\(['\"]?([^'\")]+\.(?:woff2?|ttf|otf|eot)[^'\")]*)", css)))
        rec["font_display"] = sorted(set(re.findall(r"font-display\s*:\s*([a-z]+)", css)))
        rec["font_faces"] = len(re.findall(r"@font-face", css))
        open(OUT + "/c2_" + re.sub(r"[^a-zA-Z0-9]+", "_", a)[:60] + ".css", "w", encoding="utf-8").write(css)
    res["assets"].append(rec); print(rec["status"], a, rec["bytes"], rec.get("font_faces"), flush=True); time.sleep(1.5)
json.dump(res, open(OUT + "/crawl2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
