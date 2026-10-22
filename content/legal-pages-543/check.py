import sys, json
from playwright.sync_api import sync_playwright

B = 'https://ne-prosto.ru/'
OUT = sys.argv[1]
SEND = '--send' in sys.argv
res = {}

def shot(p, name, sel=None):
    if sel:
        p.locator(sel).first.scroll_into_view_if_needed()
        p.locator(sel).first.screenshot(path=f'{OUT}/{name}.png')
    else:
        p.screenshot(path=f'{OUT}/{name}.png', full_page=False)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    for vw, vh, tag in [(1440, 900, 'd'), (390, 844, 'm')]:
        ctx = br.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=1, is_mobile=(tag == 'm'), has_touch=(tag == 'm'))
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        r = {}
        # Обсудить проект
        p.goto(B + 'koordinatyi', wait_until='networkidle')
        shot(p, f'request-{tag}', '#request')
        cb = p.locator('#request input[type=checkbox][name=policy]')
        r['request_cb_visible'] = cb.is_visible()
        p.fill('#np-name', 'Тест #543'); p.fill('#np-contact', 'test543@example.com'); p.fill('#np-message', 'тест, не отвечать')
        r['request_valid_without_cb'] = p.evaluate("document.querySelector('#request form').checkValidity()")
        p.click('#request input[type=submit]'); p.wait_for_timeout(1500)
        r['request_after_click_no_cb'] = p.locator('#request .form__results').inner_text()
        r['hscroll'] = p.evaluate('document.documentElement.scrollWidth > innerWidth')
        # обход браузерной проверки → сервер
        if tag == 'd':
            p.evaluate("document.querySelector('#request input[type=checkbox][name=policy]').removeAttribute('required')")
            p.click('#request input[type=submit]'); p.wait_for_timeout(4000)
            r['request_server_no_cb'] = p.locator('#request .form__results').inner_text()
            if SEND:
                p.check('#request input[type=checkbox][name=policy]'); p.click('#request input[type=submit]'); p.wait_for_timeout(5000)
                r['request_send_with_cb'] = p.locator('#request .form__results').inner_text()
        # подвал
        shot(p, f'footer-{tag}', 'footer.np-footer')
        r['footer_links'] = p.eval_on_selector_all('.np-footer__legal a', 'a=>a.map(x=>x.href)')
        # CTA в статье
        p.goto(B + 'blog/kuda-propadayut-zayavki-iz-messendzherov', wait_until='networkidle')
        cta = p.locator('aside.np-cta--end')
        cta.locator('summary').first.click(); p.wait_for_timeout(500)
        shot(p, f'cta-{tag}', 'aside.np-cta--end')
        f = cta.locator('form')
        f.locator('input[name=name]').fill('Тест #543'); f.locator('input[name=contact]').fill('test543@example.com')
        f.locator('textarea').fill('тест, не отвечать')
        r['cta_valid_without_cb'] = f.evaluate('f=>f.checkValidity()')
        if tag == 'd':
            f.evaluate("f=>f.querySelector('input[type=checkbox][name=policy]').removeAttribute('required')")
            f.locator('button[type=submit]').click(); p.wait_for_timeout(4000)
            r['cta_server_no_cb'] = [f.locator('.error_policy').inner_text(), cta.evaluate('e=>e.className')]
            if SEND:
                f.locator('input[type=checkbox][name=policy]').check(); f.locator('button[type=submit]').click(); p.wait_for_timeout(5000)
                r['cta_send_with_cb'] = cta.inner_text()[:300]
        # Вакансии
        p.goto(B + 'kompaniya/vakansii/', wait_until='networkidle')
        p.locator('.jobs__button--form-show').first.click(); p.wait_for_timeout(800)
        shot(p, f'job-{tag}', '.jobs__form >> nth=0')
        if tag == 'd':
            jf = p.locator('.jobs__form form').first
            jf.locator('input[name=name]').fill('Тест #543'); jf.locator('input[name=contact]').fill('test543@example.com')
            jf.locator('textarea[name=message]').fill('тест, не отвечать, проверка формы')
            r['job_valid_without_cb'] = jf.evaluate('f=>f.checkValidity()')
            jf.evaluate("f=>f.querySelector('input[type=checkbox][name=policy]').removeAttribute('required')")
            jf.locator('input[type=submit]').click(); p.wait_for_timeout(4000)
            r['job_server_no_cb'] = jf.locator('.form__results').inner_text()
        # документы
        for u in ['politika-konfidencialnosti', 'soglasie-na-obrabotku-personalnyh-dannyh']:
            p.goto(B + u, wait_until='networkidle'); shot(p, f'{u[:8]}-{tag}')
            r[u] = [p.title(), p.locator('h1').count(), p.evaluate('document.documentElement.scrollWidth > innerWidth')]
        r['js_errors'] = errs
        res[tag] = r
        ctx.close()
    br.close()
print(json.dumps(res, ensure_ascii=False, indent=1))
