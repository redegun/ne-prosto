import sys, json
from playwright.sync_api import sync_playwright

URLS = sys.argv[1].split(',')
SUBMIT = len(sys.argv) > 2 and sys.argv[2] == 'submit'
SIZES = [(1920, 1080, 'd1920'), (1440, 900, 'd1440'), (390, 844, 'm390')]
out = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for url in URLS:
        slug = url.rstrip('/').split('/')[-1].replace('.html', '')
        for w, h, tag in SIZES:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, is_mobile=w < 500, has_touch=w < 500)
            pg = ctx.new_page(); errs = []
            pg.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const b=document.body.firstElementChild;if(b&&b.textContent.startsWith('Черновик'))b.style.position='static'})")
            pg.on('pageerror', lambda e: errs.append(str(e)))
            r = pg.goto(url, wait_until='networkidle')
            info = pg.evaluate('''() => {
              const q=s=>[...document.querySelectorAll(s)];
              const ctas=q('.np-cta').map(a=>{const r=a.getBoundingClientRect();return {cls:a.className,x:Math.round(r.left),w:Math.round(r.width),top:Math.round(r.top+scrollY)}});
              const h2=q('.article-content h2').map(h=>Math.round(h.getBoundingClientRect().top+scrollY));
              const sim=document.querySelector('.article-similar');
              return {ctas,h2,sim:sim?Math.round(sim.getBoundingClientRect().top+scrollY):null,
                overflow:document.documentElement.scrollWidth>innerWidth, toc:q('.np-toc a').length,
                tocTexts:q('.np-toc a').map(a=>a.textContent).join('|').includes('Разобрать')}
            }''')
            # open mid
            mid = pg.locator('.np-cta--mid summary')
            if mid.count():
                mid.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
                mid.click(); pg.wait_for_timeout(400)
                pg.locator('.np-cta--mid').screenshot(path=f'shot-{slug}-{tag}-mid.png')
                info['midFormVisible'] = pg.locator('#np-cta-mid-form').is_visible()
                info['focus'] = pg.evaluate('document.activeElement && document.activeElement.id')
                # empty submit must be blocked by required
                if pg.locator('#np-cta-mid-form button[type=submit]').count(): pg.locator('#np-cta-mid-form button[type=submit]').click(); pg.wait_for_timeout(500)
                info['emptyBlocked'] = pg.evaluate("document.querySelector('#np-cta-mid-name').matches(':invalid') && !document.querySelector('.np-cta--mid').classList.contains('is-sent')")
                if SUBMIT and tag == 'd1440':
                    pg.fill('#np-cta-mid-name', 'ТЕСТ #538 (не отвечать)')
                    pg.fill('#np-cta-mid-contact', 'тест@test.local')
                    pg.fill('#np-cta-mid-message', 'тест: проверка формы призыва в статье блога, задача #538. Отвечать не нужно.')
                    pg.locator('#np-cta-mid-form button[type=submit]').click(); pg.wait_for_timeout(4000)
                    info['submitResult'] = pg.locator('.np-cta--mid .np-cta__result').inner_text()
                    info['sent'] = pg.evaluate("document.querySelector('.np-cta--mid').classList.contains('is-sent')")
                    pg.locator('.np-cta--mid').screenshot(path=f'shot-{slug}-{tag}-mid-sent.png')
            end = pg.locator('.np-cta--end')
            if end.count():
                end.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
                end.screenshot(path=f'shot-{slug}-{tag}-end.png')
                pg.locator('.np-cta--end summary').click(); pg.wait_for_timeout(300)
                info['endFormVisible'] = pg.locator('#np-cta-end-form').is_visible()
                end.screenshot(path=f'shot-{slug}-{tag}-end-open.png')
            pg.screenshot(path=f'shot-{slug}-{tag}-full.png', full_page=True)
            info.update(url=url, size=tag, status=r.status if r else None, errs=errs)
            out.append(info); ctx.close()
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
