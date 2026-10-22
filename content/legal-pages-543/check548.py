import sys, json
from playwright.sync_api import sync_playwright
B = 'https://ne-prosto.ru/'
OUT = sys.argv[1]
PAGES = ['', 'index-new', 'koordinatyi', 'uslugi/ii-assistent-dlya-biznesa', 'kompaniya/vakansii/', 'blog/kuda-propadayut-zayavki-iz-messendzherov']
res = {}
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for vw, vh, tag in [(1440, 900, 'd'), (390, 844, 'm')]:
        ctx = br.new_context(viewport={'width': vw, 'height': vh}, is_mobile=(tag == 'm'), has_touch=(tag == 'm'))
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        for u in PAGES:
            p.goto(B + u, wait_until='networkidle')
            # раскрыть свёрнутые формы (CTA details, вакансии)
            p.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
            for b in p.locator('.jobs__button--form-show').all():
                try: b.click(); p.wait_for_timeout(400)
                except Exception: pass
            forms = p.locator('form')
            out = []
            for i in range(forms.count()):
                f = forms.nth(i)
                info = f.evaluate("""f=>{const cb=f.querySelector('input[type=checkbox][name=policy]');
                  const hid=f.querySelector('input[type=hidden][name=policy]');
                  const lab=cb?(cb.closest('label')||cb.parentElement):null;
                  return {id:f.id||f.className, cb:!!cb, required:cb?cb.required:null, hidden:!!hid,
                    links:lab?[...lab.querySelectorAll('a')].map(a=>a.getAttribute('href')):[],
                    text:lab?lab.innerText.trim():'', note:f.innerText.includes('* обязательные поля')}}""")
                # заполнить и проверить браузерную валидацию без галочки
                f.evaluate("""f=>{for(const el of f.querySelectorAll('input[type=text],input[type=email],input[type=tel],input:not([type]),textarea')){
                    if(el.name==='name')el.value='тест #548';else if(el.type==='email'||/contact|mail|phone/.test(el.name))el.value='test548@example.com';else el.value='тест, не отвечать, проверка формы #548';}}""")
                info['valid_without_cb'] = f.evaluate('f=>f.checkValidity()')
                if tag == 'd':
                    f.evaluate("f=>{const c=f.querySelector('input[type=checkbox][name=policy]'); if(c){c.required=false;c.checked=false}}")
                    btn = f.locator('[type=submit]').first
                    btn.scroll_into_view_if_needed(); btn.click(); p.wait_for_timeout(4500)
                    info['server_reply'] = f.evaluate("f=>{const t=(f.closest('section,aside,.jobs__form')||f.parentElement).innerText; return t.split(String.fromCharCode(10)).filter(l=>/соглас|отправлен|спасибо|ошибк/i.test(l)).slice(0,4)}")
                out.append(info)
            res[f'{tag}:{u or "/"}'] = out
            res[f'{tag}:{u or "/"}:hscroll'] = p.evaluate('document.documentElement.scrollWidth > innerWidth')
        # скрины примеров
        for name, u, sel in [('request', 'koordinatyi', '#request'), ('cta', 'blog/kuda-propadayut-zayavki-iz-messendzherov', 'aside.np-cta--end'), ('job', 'kompaniya/vakansii/', '.jobs__form >> nth=0'), ('ii', 'uslugi/ii-assistent-dlya-biznesa', 'form')]:
            p.goto(B + u, wait_until='networkidle')
            p.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
            if name == 'job': p.locator('.jobs__button--form-show').first.click(); p.wait_for_timeout(600)
            el = p.locator(sel).first; el.scroll_into_view_if_needed(); p.wait_for_timeout(300)
            el.screenshot(path=f'{OUT}/{name}-{tag}.png')
        res[f'{tag}:js_errors'] = errs
        ctx.close()
    br.close()
print(json.dumps(res, ensure_ascii=False, indent=1))
