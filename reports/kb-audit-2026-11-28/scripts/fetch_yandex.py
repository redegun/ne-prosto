#!/usr/bin/env python3
"""Read-only выгрузка Вебмастера и Метрики для ne-prosto.ru (#5182). Запуск на supabase-vps: python3 - < fetch_yandex.py
Токен METRIKA_TOKEN читается из /var/www/seo-dashboard/.env и не печатается. Вывод — JSON в stdout."""
import json, urllib.request, urllib.parse, sys, time, socket
_gai = socket.getaddrinfo
def _gai4(host, *a, **k):  # IPv6 с supabase-vps висит в SYN-SENT — только IPv4
    return [r for r in _gai(host, *a, **k) if r[0] == socket.AF_INET] or _gai(host, *a, **k)
socket.getaddrinfo = _gai4

TOKEN = None
for line in open("/var/www/seo-dashboard/.env", encoding="utf-8"):
    line = line.strip()
    if line.startswith("METRIKA_TOKEN="):
        TOKEN = line.split("=", 1)[1].strip().strip("\"'")
if not TOKEN:
    print(json.dumps({"error": "no token"}))
    sys.exit(0)

UID = 247161245
HOST = "https:ne-prosto.ru:443"
CID = 27066311
D1, D2 = "2026-10-29", "2026-11-27"
WMB = "https://api.webmaster.yandex.net/v4/user/%d/hosts/%s" % (UID, urllib.parse.quote(HOST, safe=""))


def get(url, params=None):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"Authorization": "OAuth " + TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")[:400]
        except Exception:
            body = ""
        return {"_http_error": e.code, "_body": body}
    except Exception as e:
        return {"_error": str(e)}


out = {"window": [D1, D2]}
wm = {}
wm["hosts_found"] = [h for h in (get("https://api.webmaster.yandex.net/v4/user/%d/hosts" % UID).get("hosts") or [])
                     if "ne-prosto" in (h.get("host_id") or "")]
for name, path, params in [
    ("host", "", None),
    ("summary", "/summary", None),
    ("diagnostics", "/diagnostics", None),
    ("sqi_history", "/sqi-history", {"date_from": "2026-05-01", "date_to": D2}),
    ("in_search_history", "/search-urls/in-search/history", {"date_from": "2026-08-01", "date_to": D2}),
    ("in_search_samples", "/search-urls/in-search/samples", {"offset": 0, "limit": 100}),
    ("events_history", "/search-urls/events/history", {"date_from": "2026-09-01", "date_to": D2}),
    ("events_samples", "/search-urls/events/samples", {"offset": 0, "limit": 100}),
    ("indexing_history", "/indexing/history", {"date_from": "2026-09-01", "date_to": D2}),
    ("indexing_samples", "/indexing/samples", {"offset": 0, "limit": 100}),
    ("sitemaps", "/sitemaps", None),
    ("user_sitemaps", "/user-added-sitemaps", None),
    ("important_urls", "/important-urls", None),
    ("links_internal_broken", "/links/internal/broken/samples", {"offset": 0, "limit": 100}),
    ("links_internal_broken_history", "/links/internal/broken/history", {"date_from": "2026-08-01", "date_to": D2}),
    ("links_external", "/links/external/samples", {"offset": 0, "limit": 100}),
    ("links_external_history", "/links/external/history", {"indicator": "LINKS_TOTAL_COUNT"}),
    ("recrawl_quota", "/recrawl/quota", None),
    ("popular_queries", "/search-queries/popular", {"order_by": "TOTAL_SHOWS",
                                                     "query_indicator": ["TOTAL_SHOWS", "TOTAL_CLICKS", "AVG_SHOW_POSITION", "AVG_CLICK_POSITION"],
                                                     "date_from": "2026-11-01", "date_to": D2, "limit": 500}),
    ("popular_queries_oct", "/search-queries/popular", {"order_by": "TOTAL_SHOWS",
                                                         "query_indicator": ["TOTAL_SHOWS", "TOTAL_CLICKS", "AVG_SHOW_POSITION"],
                                                         "date_from": "2026-09-01", "date_to": "2026-10-31", "limit": 500}),
    ("queries_history", "/search-queries/all/history", {"query_indicator": ["TOTAL_SHOWS", "TOTAL_CLICKS"],
                                                         "date_from": "2026-08-01", "date_to": D2}),
]:
    wm[name] = get(WMB + path, params)
    time.sleep(0.3)
out["webmaster"] = wm

# ---- Метрика
ST = "https://api-metrika.yandex.net/stat/v1/data"
NR = "ym:s:isRobot=='No'"
m = {}
m["counter"] = get("https://api-metrika.yandex.net/management/v1/counter/%d" % CID)
goals = get("https://api-metrika.yandex.net/management/v1/counter/%d/goals" % CID)
m["goals"] = [{"id": g.get("id"), "name": g.get("name"), "type": g.get("type"), "conditions": g.get("conditions")}
              for g in (goals.get("goals") or [])]


def q(name, metrics, dims=None, filters=NR, limit=50, sort=None, d1=D1, d2=D2, group=None):
    p = {"ids": CID, "date1": d1, "date2": d2, "metrics": metrics, "limit": limit, "accuracy": "full"}
    if dims:
        p["dimensions"] = dims
    if filters:
        p["filters"] = filters
    if sort:
        p["sort"] = sort
    if group:
        p["group"] = group
    r = get(ST, p)
    if "data" in r:
        r = {"totals": r.get("totals"), "query": {"dimensions": r.get("query", {}).get("dimensions"),
                                                  "metrics": r.get("query", {}).get("metrics")},
             "rows": [{"dims": [d.get("name") for d in row.get("dimensions", [])], "metrics": row.get("metrics")}
                      for row in r.get("data", [])]}
    m[name] = r
    time.sleep(0.3)


VM = "ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds"
q("totals", VM)
q("by_source", VM, "ym:s:lastTrafficSource")
q("by_device", VM, "ym:s:deviceCategory")
q("organic_by_engine", VM, "ym:s:lastSearchEngineRoot", filters=NR + " AND ym:s:lastTrafficSource=='organic'")
q("organic_by_device", VM, "ym:s:deviceCategory", filters=NR + " AND ym:s:lastTrafficSource=='organic'")
q("organic_landing", VM, "ym:s:startURLPath", filters=NR + " AND ym:s:lastTrafficSource=='organic'", limit=60, sort="-ym:s:visits")
q("all_landing", VM, "ym:s:startURLPath", limit=60, sort="-ym:s:visits")
q("organic_monthly", "ym:s:visits", "ym:s:lastSearchEngineRoot", filters=NR + " AND ym:s:lastTrafficSource=='organic'",
  d1="2026-03-01", d2=D2, group="month", limit=10)
q("visits_by_month", "ym:s:visits", None, d1="2026-03-01", d2=D2, group="month")
q("search_phrases", "ym:s:visits", "ym:s:lastSearchPhrase", filters=NR + " AND ym:s:lastTrafficSource=='organic'", limit=50, sort="-ym:s:visits")
q("regions", "ym:s:visits", "ym:s:regionCity", limit=15, sort="-ym:s:visits")
# цели: по 10 метрик за запрос
ids = [g["id"] for g in m["goals"]]
reach = {}
for i in range(0, len(ids), 10):
    chunk = ids[i:i + 10]
    met = ",".join("ym:s:goal%dreaches" % g for g in chunk)
    p = {"ids": CID, "date1": D1, "date2": D2, "metrics": met, "filters": NR, "accuracy": "full"}
    r = get(ST, p)
    tot = r.get("totals") or []
    for g, v in zip(chunk, tot):
        reach[str(g)] = v
    time.sleep(0.3)
m["goal_reaches_30d"] = reach
# цели по месяцам
mon = {}
for g in [x["id"] for x in m["goals"]]:
    p = {"ids": CID, "date1": "2026-06-01", "date2": D2, "metrics": "ym:s:goal%dreaches" % g, "filters": NR,
         "group": "month", "dimensions": "ym:s:month", "accuracy": "full"}
    r = get(ST, p)
    mon[str(g)] = [{"m": [d.get("name") for d in row.get("dimensions", [])], "v": row.get("metrics")} for row in r.get("data", [])] if "data" in r else r
    time.sleep(0.3)
m["goal_monthly"] = mon
# отказы органики по типу страниц
q("organic_landing_bounce_articles", VM, "ym:s:startURLPath",
  filters=NR + " AND ym:s:lastTrafficSource=='organic' AND ym:s:startURLPath=~'^/blog/'", limit=40, sort="-ym:s:visits")
q("organic_landing_bounce_services", VM, "ym:s:startURLPath",
  filters=NR + " AND ym:s:lastTrafficSource=='organic' AND ym:s:startURLPath=~'^/(uslugi|podderzhka)/'", limit=40, sort="-ym:s:visits")
q("by_day", "ym:s:visits", "ym:s:date", d1="2026-11-01", d2=D2, limit=40, sort="ym:s:date")
q("referrals", "ym:s:visits", "ym:s:lastReferalSource", filters=NR + " AND ym:s:lastTrafficSource=='referral'", limit=30, sort="-ym:s:visits")
q("robots_share", "ym:s:visits", "ym:s:isRobot", filters=None, limit=5)
q("pageviews_top", "ym:pv:pageviews", "ym:pv:URLPath", filters=None, limit=40, sort="-ym:pv:pageviews")
out["metrika"] = m
print(json.dumps(out, ensure_ascii=False, default=str))
