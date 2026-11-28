#!/usr/bin/env python3
"""Read-only GSC для ne-prosto.ru (#5182): Search Analytics 28 дней, sitemaps, URL Inspection выборки.
Запуск на clou-server: /root/.openclaw/venv/reports/bin/python - < fetch_gsc.py"""
import json, sys, time
from google.oauth2 import service_account
from googleapiclient.discovery import build

SA_PATH = "/root/.openclaw/secrets/google-service-account.json"
PROP = None
D1, D2 = "2026-10-29", "2026-11-25"
creds = service_account.Credentials.from_service_account_file(
    SA_PATH, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
sites = svc.sites().list().execute().get("siteEntry", [])
cand = [s for s in sites if "ne-prosto" in s.get("siteUrl", "")]
out = {"sites_found": cand, "window": [D1, D2]}
for s in cand:
    if s.get("permissionLevel") != "siteUnverifiedUser":
        PROP = s["siteUrl"]
        break
out["property"] = PROP
if not PROP:
    print(json.dumps(out, ensure_ascii=False)); sys.exit(0)


def sa(dims, limit=250, d1=D1, d2=D2, filters=None):
    body = {"startDate": d1, "endDate": d2, "dimensions": dims, "rowLimit": limit}
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]
    try:
        return svc.searchanalytics().query(siteUrl=PROP, body=body).execute().get("rows", [])
    except Exception as e:
        return {"error": str(e)[:300]}


out["totals"] = sa([], 1)
out["by_query"] = sa(["query"], 300)
out["by_page"] = sa(["page"], 300)
out["by_device"] = sa(["device"], 10)
out["by_month"] = sa(["date"], 400, d1="2026-06-01", d2=D2)
out["by_query_page_90"] = sa(["query", "page"], 500, d1="2026-08-28", d2=D2)
out["by_page_90"] = sa(["page"], 300, d1="2026-08-28", d2=D2)
try:
    out["sitemaps"] = svc.sitemaps().list(siteUrl=PROP).execute()
except Exception as e:
    out["sitemaps"] = {"error": str(e)[:300]}

URLS = [
    "https://ne-prosto.ru/",
    "https://ne-prosto.ru/uslugi/sajtyi",
    "https://ne-prosto.ru/uslugi/ii-assistent-dlya-biznesa",
    "https://ne-prosto.ru/uslugi/logotipyi-firmennyie-stili",
    "https://ne-prosto.ru/podderzhka/prodvizhenie",
    "https://ne-prosto.ru/portfolio/vinyl-tm",
    "https://ne-prosto.ru/blog/etapy-razrabotki-sajta",
    "https://ne-prosto.ru/blog/semanticheskoe-yadro-sajta",
    "https://ne-prosto.ru/blog/besplatnye-kirillicheskie-shrifty",
    "https://ne-prosto.ru/koordinatyi",
]
insp = []
for u in URLS:
    try:
        r = svc.urlInspection().index().inspect(body={"inspectionUrl": u, "siteUrl": PROP, "languageCode": "ru"}).execute()
        ir = r.get("inspectionResult", {})
        idx = ir.get("indexStatusResult", {})
        mob = ir.get("mobileUsabilityResult", {})
        rich = ir.get("richResultsResult", {})
        insp.append({"url": u, "verdict": idx.get("verdict"), "coverageState": idx.get("coverageState"),
                     "robotsTxtState": idx.get("robotsTxtState"), "indexingState": idx.get("indexingState"),
                     "lastCrawlTime": idx.get("lastCrawlTime"), "pageFetchState": idx.get("pageFetchState"),
                     "googleCanonical": idx.get("googleCanonical"), "userCanonical": idx.get("userCanonical"),
                     "crawledAs": idx.get("crawledAs"), "sitemap": idx.get("sitemap"),
                     "mobile": mob.get("verdict"), "rich": rich.get("verdict"),
                     "rich_items": [(d.get("richResultType"), [i.get("issueMessage") for it in d.get("items", []) for i in it.get("issues", [])])
                                    for d in rich.get("detectedItems", [])]})
    except Exception as e:
        insp.append({"url": u, "error": str(e)[:300]})
    time.sleep(0.5)
out["inspection"] = insp
print(json.dumps(out, ensure_ascii=False, default=str))
