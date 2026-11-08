import json, base64
from pathlib import Path

ALT = 'np-vinyl-marki,np-vinyl-goroda,np-vinyl-raboty'
NP_OLD = "{set $ss = ['n' => 'np-vinyl', 'bg' => '#e9ecef', 'l' => 'Калькулятор стоимости оклейки на сайте Vinyl-TM и рост визитов из поиска']}"
NP_NEW = "{set $ss = ['n' => 'np-vinyl', 'bg' => '#e9ecef', 'l' => 'Калькулятор стоимости оклейки на сайте Vinyl-TM и рост визитов из поиска', 'alt' => '" + ALT + "']}"
V_OLD = '<video muted loop playsinline preload="none" width="1440" height="1080" data-poster="/assets/neprosto/stageshow/{$ss.n}/poster-1440.png"'
V_NEW = '<video muted loop playsinline preload="none" width="1440" height="1080"{if $ss.alt?} data-ss-alt="{$ss.alt}"{/if} data-poster="/assets/neprosto/stageshow/{$ss.n}/poster-1440.png"'

H2 = 'font-size:26px;font-weight:800;line-height:1.2;margin:44px 0 12px;'
P = 'font-size:18px;line-height:1.6;max-width:780px;margin:0 0 24px;'
SECTIONS = [
    ('np-vinyl-marki', 'Раздел «Марки»: страницы по одному эталону',
     'Переделали 12 страниц марок по одному эталону: на каждой тарифы, калькулятор, кейсы с этой маркой и частые вопросы. '
     'Добавили шесть марок, по которым было больше всего работ, но не было своей страницы: ГАЗ, Fiat, IVECO, Škoda, Sollers и Toyota.',
     'Раздел «Марки» на сайте Vinyl-TM: 12 страниц марок по одному эталону и 6 новых'),
    ('np-vinyl-goroda', 'Страницы по городам',
     'Прошли по одному регламенту страницы 46 городов. У каждой свой заголовок и тексты под город, четыре тарифа и шесть примеров работ. '
     'Работы берутся по очереди из общего списка, поэтому соседние города не показывают одно и то же.',
     'Страницы Vinyl-TM по городам: свой заголовок, тарифы и примеры работ, 46 городов'),
    ('np-vinyl-raboty', 'Каталог работ',
     'На сайте больше 580 страниц выполненных работ: фото, модель, тариф. Сделали конструктор, который выводит эти работы на любой странице, '
     'так что на страницах марок, городов и услуг сразу видны настоящие примеры.',
     'Каталог работ Vinyl-TM: 580+ страниц работ по видам транспорта'),
]
block = ''
for n, h, p, l in SECTIONS:
    block += (f'<h2 style="{H2}">{h}</h2><p style="{P}">{p}</p>\n'
              f'[[$np_ss_case? &name=`{n}` &bg=`#e9ecef` &label=`{l}`]]\n')
ANCHOR = '<div style="margin:0 0 30px;"><div style="font-size:22px;font-weight:800;margin:0 0 18px;">Над проектом работали</div>'

data = {'np_old': NP_OLD, 'np_new': NP_NEW, 'v_old': V_OLD, 'v_new': V_NEW,
        'anchor': ANCHOR, 'block': block, 'js_old': 'stageshow.js?v=1', 'js_new': 'stageshow.js?v=2'}
tpl = Path('apply.tpl.php').read_text(encoding='utf-8')
tpl = tpl.replace('@@DATA@@', base64.b64encode(json.dumps(data, ensure_ascii=False).encode()).decode())
Path('apply.php').write_text(tpl, encoding='utf-8', newline='\n')
Path('sections.html').write_text(block, encoding='utf-8', newline='\n')
print('ok', len(tpl))
