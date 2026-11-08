import json, base64
from pathlib import Path
CASES = {
    'lrrazbor-poisk': ('np-lrrazbor', '#e9edf3', 'Поиск LRrazbor: по запросу «суппорт дискавери 3» вместо «ничего не найдено» — 53 детали'),
    'firmaflis': ('np-flis', '#e8e5dd', 'ФЛиС: каталог спецодежды с мега-меню и фильтрами, 92 SEO-описания товаров'),
    'muza': ('np-muza', '#ead9c6', 'Муза: онлайн-запись в салон, услуги и мастера каждый день из YClients'),
}
OLD_SHA = 'ce0a7683bd99a4d962425b8985ad49200bae0e2c19e3efe5de78fdd34d77c3bd'
ANCHOR = "{/if}{if $ss?}"
add = ''.join("{elseif $uri == 'portfolio/" + s + "'}{set $ss = ['n' => '" + n + "', 'bg' => '" + bg + "', 'l' => '" + l + "']}"
              for s, (n, bg, l) in CASES.items())


def call(s):
    n, bg, l = CASES[s]
    return '[[$np_ss_case? &name=`' + n + '` &bg=`' + bg + '` &label=`' + l + '`]]'


muza_body = (
    '<div style="display:flex;flex-wrap:wrap;gap:14px;margin:0 0 30px;">'
    '<div style="flex:1 1 160px;background:#111;border-radius:14px;padding:24px 22px;"><div style="font-size:32px;font-weight:800;line-height:1.05;color:#fff;">Tilda → MODX</div><div style="font-size:14px;line-height:1.4;margin-top:10px;color:rgba(255,255,255,.75);">переезд сайта<br>салона</div></div>'
    '<div style="flex:1 1 160px;background:#f4f5f7;border-radius:14px;padding:24px 22px;"><div style="font-size:32px;font-weight:800;line-height:1.05;color:#111;">200+</div><div style="font-size:14px;line-height:1.4;margin-top:10px;color:#6b7280;">услуг с ценами<br>из YClients</div></div>'
    '<div style="flex:1 1 160px;background:#f4f5f7;border-radius:14px;padding:24px 22px;"><div style="font-size:32px;font-weight:800;line-height:1.05;color:#111;">каждый день</div><div style="font-size:14px;line-height:1.4;margin-top:10px;color:#6b7280;">обновляются услуги,<br>цены и мастера</div></div></div>'
    '<p style="font-size:18px;line-height:1.6;max-width:780px;margin:0 0 30px;">Перевезли сайт салона красоты в Благовещенске с Tilda на MODX. Услуги, цены и мастера каждый день подтягиваются из YClients, а записаться можно прямо со страницы услуги. Сделали страницы 48 разделов, карточки мастеров с работами и сертификатами, акции на главной, подключили Метрику с целями на запись и звонки.</p>'
    '<img src="images/portfolio/clients/muza.jpg" alt="Скриншот сайта" style="display:block;width:100%;height:auto;border-radius:10px;margin:0 0 26px;">'
    '<p><a href="https://salonmuza.ru/" target="_blank" rel="noopener nofollow" style="display:inline-block;padding:14px 30px;background:#111;color:#fff;text-decoration:none;border-radius:8px;font-weight:600;">Открыть сайт &rarr;</a></p>')
data = {
    'old_sha': OLD_SHA, 'anchor': ANCHOR, 'add': add,
    'res': {'92': {'sha': '3172aa5b606bba02692e509e872886280cf26d02852bd3999b9479658d918d3b', 'call': call('firmaflis')},
            '101': {'sha': '37028f4a3583a8e66b79fb0a0a3e6ed8fc22ce4268a05aab77da98468b199f90', 'call': call('lrrazbor-poisk')}},
    'muza': {'pagetitle': 'Разработка и SEO — «Муза»', 'alias': 'muza',
             'introtext': 'Сайт салона красоты «Муза»: переезд с Tilda на MODX, услуги и запись из YClients',
             'content': call('muza') + '\n' + muza_body, 'image': 'images/portfolio/clients/muza-card.jpg'},
}
tpl = Path('apply.tpl.php').read_text(encoding='utf-8')
tpl = tpl.replace('@@DATA@@', base64.b64encode(json.dumps(data, ensure_ascii=False).encode()).decode())
Path('apply.php').write_text(tpl, encoding='utf-8', newline='\n')
print('ok', len(tpl))
