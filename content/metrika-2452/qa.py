"""task 2452: живая проверка Метрики 27066311 на ne-prosto.ru (office1080, Playwright).
Все POST на ne-prosto.ru перехватываются и получают поддельный успех AjaxForm — письма не уходят."""
import json, re, sys, time
from urllib.parse import unquote, urlparse
from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
BASE = "https://ne-prosto.ru"
res = {}


def run(page_url, name, act, width=1440, height=900):
    hits, posts, errors = [], [], []
    ctx = br.new_context(viewport={"width": width, "height": height}, locale="ru-RU")
    page = ctx.new_page()

    def route(r):
        req = r.request
        if req.method == "POST" and urlparse(req.url).hostname == "ne-prosto.ru":
            posts.append(req.url)
            r.fulfill(status=200, content_type="application/json; charset=utf-8",
                      body=json.dumps({"success": True, "message": "Тест task2452: письмо не отправлялось", "data": []}))
        else:
            r.continue_()

    page.route("**/*", route)
    page.on("request", lambda q: hits.append(unquote(q.url)) if "mc.yandex" in q.url else None)
    page.on("pageerror", lambda e: errors.append(str(e)[:200]))
    page.goto(BASE + page_url, wait_until="load", timeout=60000)
    page.wait_for_timeout(4000)
    r = {"url": page_url, "ym_defined": page.evaluate("typeof window.ym === 'function'"),
         "tag_js": any("metrika/tag.js" in h for h in hits),
         "pageview_hit": any(re.search(r"/watch/27066311", h) and "goal://" not in h for h in hits)}
    if act:
        try:
            act(page)
            page.wait_for_timeout(4000)
        except Exception as e:  # noqa
            r["act_error"] = str(e)[:300]
    goals = sorted({m.group(1) for h in hits for m in [re.search(r"goal://[^/]+/([a-z_]+)", h)] if m})
    r.update({"goals": goals, "mock_posts": posts, "js_errors": errors,
              "overflow": page.evaluate("document.documentElement.scrollWidth > window.innerWidth"),
              "h1": page.locator("h1").count()})
    page.screenshot(path=f"{OUT}/{name}-{width}.png", full_page=False)
    ctx.close()
    res[f"{name}-{width}"] = r
    print(name, width, json.dumps(r, ensure_ascii=False))


def home_form(page):
    f = page.locator("form.request-form").first
    f.scroll_into_view_if_needed()
    f.locator("input[name=name]").fill("Тест task2452")
    f.locator("input[name=contact]").fill("test2452@example.com")
    f.locator("input[type=checkbox][name=policy]").check()
    f.locator("input[type=submit]").click()


def cta_form(page):
    f = page.locator("form.np-cta-form").first
    page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    f.scroll_into_view_if_needed()
    for inp in f.locator("input:not([type=hidden]):not([type=checkbox]):not([type=submit]), textarea").all():
        if not inp.is_visible():
            continue
        t = (inp.get_attribute("type") or "").lower()
        nm = (inp.get_attribute("name") or "")
        if nm == "email":  # антиспам-ловушка
            continue
        inp.fill("test2452@example.com" if t == "email" or "mail" in nm or "contact" in nm else ("+7 900 000-00-00" if t == "tel" else "Тест task2452"))
    for cb in f.locator("input[type=checkbox]").all():
        if cb.is_visible():
            cb.check()
    f.locator("[type=submit]").first.click()


def job_form(page):
    page.locator(".jobs__button--form-show").first.click()
    page.wait_for_timeout(800)
    f = page.locator(".jobs__form form").first
    for inp in f.locator("input:not([type=hidden]):not([type=checkbox]):not([type=submit]):not([type=file]), textarea").all():
        if not inp.is_visible():
            continue
        nm = (inp.get_attribute("name") or "")
        if nm == "email" and not inp.is_visible():
            continue
        t = (inp.get_attribute("type") or "").lower()
        inp.fill("test2452@example.com" if t == "email" or "mail" in nm or "contact" in nm else ("+7 900 000-00-00" if t == "tel" or "phone" in nm else "Тест task2452"))
    for cb in f.locator("input[type=checkbox]").all():
        if cb.is_visible():
            cb.check()
    f.locator("[type=submit]").first.click()


with sync_playwright() as p:
    br = p.chromium.launch()
    run("/", "home", home_form)
    run("/", "home", None, 390, 844)
    run("/koordinatyi", "contacts", home_form)
    run("/blog/skorost-zagruzki-sajta", "article", cta_form)
    run("/blog/skorost-zagruzki-sajta", "article", None, 390, 844)
    run("/kompaniya/vakansii/", "jobs", job_form)
    run("/politika-konfidencialnosti", "policy", None)
    run("/politika-konfidencialnosti", "policy", None, 390, 844)
    br.close()
json.dump(res, open(f"{OUT}/qa.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
