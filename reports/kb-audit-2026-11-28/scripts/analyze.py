#!/usr/bin/env python3
"""Разбор сохранённого HTML обхода #5182 → crawl/analysis.json (и краткая таблица в stdout)."""
import json, re, sys, collections
from bs4 import BeautifulSoup

D = sys.argv[1] if len(sys.argv) > 1 else "D:/project/tmp/task-5182/crawl"
crawl = json.load(open(D + "/crawl.json", encoding="utf-8"))
BASE = "https://ne-prosto.ru"
out = []


def norm(u):
    return (u or "").strip()


for p in crawl["pages"]:
    if not p.get("file"):
        out.append({"url": p["url"], "kind": p["kind"], "status": p.get("status"), "location": p.get("location")})
        continue
    html = open(D + "/html/" + p["file"], encoding="utf-8").read()
    s = BeautifulSoup(html, "lxml")
    head = s.head or s
    r = {"url": p["url"], "kind": p["kind"], "status": p["status"], "time": p["time"], "bytes": p["bytes"],
         "headers": p["headers"], "file": p["file"]}
    r["title"] = (s.title.get_text(strip=True) if s.title else None)
    md = head.find("meta", attrs={"name": re.compile("^description$", re.I)})
    r["description"] = md.get("content") if md else None
    r["robots_meta"] = [(m.get("name"), m.get("content")) for m in s.find_all("meta", attrs={"name": re.compile("robots|googlebot|yandex", re.I)})]
    r["canonical"] = [l.get("href") for l in s.find_all("link", rel=lambda v: v and "canonical" in v)]
    r["canonical_in_head"] = [l.get("href") for l in head.find_all("link", rel=lambda v: v and "canonical" in v)] if s.head else None
    r["base"] = s.base.get("href") if s.base else None
    r["viewport"] = (head.find("meta", attrs={"name": "viewport"}) or {}).get("content") if head.find("meta", attrs={"name": "viewport"}) else None
    r["h1"] = [h.get_text(" ", strip=True) for h in s.find_all("h1")]
    r["h2"] = [h.get_text(" ", strip=True)[:80] for h in s.find_all("h2")]
    r["h_seq"] = [int(h.name[1]) for h in s.find_all(re.compile("^h[1-6]$"))]
    og = {}
    for m in s.find_all("meta", attrs={"property": re.compile("^og:|^article:")}):
        og[m.get("property")] = m.get("content")
    for m in s.find_all("meta", attrs={"name": re.compile("^twitter:")}):
        og[m.get("name")] = m.get("content")
    r["og"] = og
    # JSON-LD
    lds = []
    for sc in s.find_all("script", type="application/ld+json"):
        txt = sc.string or sc.get_text() or ""
        try:
            j = json.loads(txt)
            lds.append({"ok": True, "json": j})
        except Exception as e:
            lds.append({"ok": False, "err": str(e)[:120], "raw": txt[:300]})
    r["ld"] = lds
    types = []

    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            if t:
                types.extend(t if isinstance(t, list) else [t])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for l in lds:
        if l.get("ok"):
            walk(l["json"])
    r["ld_types"] = types
    r["microdata"] = sorted(set(e.get("itemtype") for e in s.find_all(attrs={"itemtype": True})))
    # dates in ld
    dates = []
    for l in lds:
        if l.get("ok"):
            for k in ("datePublished", "dateModified"):
                for mm in re.finditer(r'"%s"\s*:\s*"([^"]*)"' % k, json.dumps(l["json"], ensure_ascii=False)):
                    dates.append((k, mm.group(1)))
    for e in s.find_all(attrs={"itemprop": re.compile("datePublished|dateModified")}):
        dates.append((e.get("itemprop") + "(md)", e.get("content") or e.get("datetime") or e.get_text(strip=True)))
    r["dates"] = dates
    # images
    imgs = s.find_all("img")
    il = []
    for i in imgs:
        src = i.get("src") or ""
        il.append({"src": src[:160], "data_src": (i.get("data-src") or "")[:160], "loading": i.get("loading"),
                   "fp": i.get("fetchpriority"), "w": i.get("width"), "h": i.get("height"),
                   "alt": i.get("alt"), "cls": " ".join(i.get("class") or [])[:60]})
    r["img_count"] = len(il)
    r["img_first"] = il[:4]
    r["img_lazy"] = sum(1 for i in il if i["loading"] == "lazy")
    r["img_no_alt"] = sum(1 for i in il if i["alt"] is None)
    r["img_empty_alt"] = sum(1 for i in il if i["alt"] is not None and not i["alt"].strip())
    r["img_no_dims"] = sum(1 for i in il if not (i["w"] and i["h"]))
    r["img_webp"] = sum(1 for i in il if ".webp" in (i["src"] + i["data_src"]).lower())
    alts = [i["alt"].strip() for i in il if i["alt"] and i["alt"].strip()]
    r["alt_dups"] = [a for a, c in collections.Counter(alts).items() if c > 1][:8]
    r["alt_short"] = [a for a in alts if len(a) < 5][:8]
    r["img_names"] = [re.sub(r".*/", "", i["src"] or i["data_src"])[:60] for i in il][:30]
    # links
    links = s.find_all("a", href=True)
    internal, external, tel, mailto, rels = [], [], [], [], collections.Counter()
    for a in links:
        h = a["href"].strip()
        rel = " ".join(a.get("rel") or [])
        if rel:
            rels[rel] += 1
        if h.startswith("tel:"):
            tel.append(h)
        elif h.startswith("mailto:"):
            mailto.append(h)
        elif h.startswith("http") and "ne-prosto.ru" not in h:
            external.append(h)
        elif h.startswith("#") or h.startswith("javascript"):
            continue
        else:
            internal.append(h)
    r["links_internal"] = len(internal)
    r["links_internal_set"] = sorted(set(internal))
    r["links_external"] = sorted(set(external))
    r["tel"] = sorted(set(tel))
    r["mailto"] = sorted(set(mailto))
    r["rels"] = dict(rels)
    r["dofollow"] = sum(1 for a in links if "dofollow" in " ".join(a.get("rel") or []).lower())
    r["relative_no_slash"] = sorted(set(h for h in internal if not h.startswith("/") and not h.startswith("http") and not h.startswith("?")))[:20]
    # scripts / goals
    r["ym_ids"] = sorted(set(re.findall(r"ym\((\d+)", html)))
    r["goals"] = sorted(set(re.findall(r"reachGoal['\"]?\s*,\s*['\"]([^'\"]+)", html)))
    r["data_goal_attrs"] = sorted(set(re.findall(r"data-[a-z0-9-]*goal[a-z0-9-]*=\"([^\"]*)\"", html)))[:20]
    r["onclick_ym"] = len(re.findall(r"onclick=\"[^\"]*ym\(", html))
    # forms
    forms = s.find_all("form")
    r["forms"] = [{"id": f.get("id"), "cls": " ".join(f.get("class") or [])[:60], "action": f.get("action"),
                   "checked": [c.get("name") for c in f.find_all("input", type="checkbox") if c.has_attr("checked")],
                   "tel_inputs": len(f.find_all("input", type="tel")), "fields": len(f.find_all(["input", "textarea", "select"]))}
                  for f in forms]
    # preload / fonts
    r["preload"] = [(l.get("href"), l.get("as")) for l in s.find_all("link", rel=lambda v: v and "preload" in v)]
    r["css"] = [l.get("href") for l in s.find_all("link", rel=lambda v: v and "stylesheet" in v)][:12]
    r["scripts"] = [sc.get("src") for sc in s.find_all("script", src=True)][:25]
    r["inline_style_in_body"] = len(s.body.find_all("style")) if s.body else None
    # text
    main = s.find("main") or s.body or s
    txt = main.get_text(" ", strip=True)
    r["words"] = len(txt.split())
    low = txt.lower()
    r["guarantee"] = sorted(set(m.group(0) for m in re.finditer(r"гаранти[а-я]*[^.]{0,40}?(\d+[,.]?\d*)\s*(лет|год|года|месяц[а-я]*)", low)))[:10]
    r["absolute_claims"] = sorted(set(m.group(0) for m in re.finditer(r"(лучш[а-я]+|№\s?1|номер один|самы[ей] [а-я]+|100\s?%|гарантируем[а-я ]{0,30}|лидер[а-я]*)", low)))[:12]
    r["prices"] = sorted(set(m.group(0) for m in re.finditer(r"от\s?\d[\d\s]{1,9}\s?(₽|руб)", low)))[:10]
    r["has_faq_words"] = bool(re.search(r"частые вопросы|вопросы и ответы|faq", low))
    r["has_short_answer"] = bool(re.search(r"коротко|кратко|главное:", low))
    r["updated_visible"] = re.findall(r"(обновлено|опубликовано|дата публикации)[:\s]*([0-9]{1,2}[.\s][0-9а-я]{2,9}[.\s][0-9]{2,4})", low)[:3]
    r["og_image"] = og.get("og:image")
    r["hreflang"] = [l.get("hreflang") for l in s.find_all("link", rel=lambda v: v and "alternate" in v) if l.get("hreflang")]
    r["icons"] = [(l.get("rel"), l.get("href")) for l in s.find_all("link", rel=lambda v: v and any("icon" in x for x in v))]
    r["breadcrumbs_html"] = bool(s.select('[class*="breadcrumb"], nav[aria-label*="крошк"], [itemtype*="BreadcrumbList"]'))
    r["tel_header"] = bool((s.find("header") or s).find("a", href=re.compile("^tel:")))
    r["cta_discuss"] = len(re.findall(r"обсудить проект", low))
    r["links_to_services"] = sorted(set(h for h in internal if re.search(r"/(uslugi|podderzhka)/", h)))
    r["links_to_blog"] = sorted(set(h for h in internal if "/blog/" in h and h.rstrip("/") not in ("/blog", "blog", "https://ne-prosto.ru/blog")))
    r["links_to_portfolio"] = sorted(set(h for h in internal if "/portfolio/" in h))
    r["author_mentions"] = sorted(set(m.group(0) for m in re.finditer(r"(автор[а-я]*[:\s]+[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+)", txt)))[:5]
    r["h2_count"] = len(r["h2"])
    r["toc"] = bool(s.select('[class*="toc"], [class*="contents"], [id*="toc"]'))
    r["time_tags"] = [(e.get("datetime"), e.get_text(" ", strip=True)[:40]) for e in s.find_all("time")][:5]
    r["header_text"] = (s.find("header").get_text(" ", strip=True)[:300] if s.find("header") else None)
    r["footer_text"] = (s.find("footer").get_text(" ", strip=True)[:500] if s.find("footer") else None)
    r["iframes"] = [f.get("src") for f in s.find_all("iframe")][:8]
    r["video"] = len(s.find_all("video"))
    r["main_present"] = bool(s.find("main"))
    r["lang"] = (s.html.get("lang") if s.html else None)
    r["meta_keywords"] = (head.find("meta", attrs={"name": "keywords"}) or {}).get("content") if head.find("meta", attrs={"name": "keywords"}) else None
    r["inline_js_bytes"] = sum(len(sc.get_text() or "") for sc in s.find_all("script") if not sc.get("src"))
    r["html_comments_test"] = len(re.findall(r"lorem|тест|test", txt.lower()))
    r["text_head"] = txt[:600]
    out.append(r)

json.dump(out, open(D + "/analysis.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in out:
    if "title" not in r:
        print(r["kind"], r["status"], r["url"], r.get("location"))
        continue
    print("%-8s %s | T(%d)=%s | D(%s) | H1=%d | can=%s | rob=%s | ld=%s | img=%d lazy=%d noalt=%d webp=%d | w=%d" % (
        r["kind"], r["url"].replace(BASE, "") or "/", len(r["title"] or ""), (r["title"] or "")[:60],
        len(r["description"] or ""), len(r["h1"]),
        "self" if r["canonical"] == [r["url"]] else r["canonical"], [x[1] for x in r["robots_meta"]],
        ",".join(sorted(set(r["ld_types"])))[:60], r["img_count"], r["img_lazy"], r["img_no_alt"], r["img_webp"], r["words"]))
