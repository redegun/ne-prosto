# task 1750: vinyl-tm — шапка кейса в относительные (×1000), главный ролик без абсолютных визитов
# (новое имя np-vinyl-calc — у старых файлов кеш на год), раздел «Органика по Метрике» + np-vinyl-organika в чередование карточки.
import json, base64
from pathlib import Path

H2 = 'font-size:26px;font-weight:800;line-height:1.2;margin:44px 0 12px;'
P = 'font-size:18px;line-height:1.6;max-width:780px;margin:0 0 24px;'

R = [  # (старое, новое) в content ресурса 83 — каждое ровно 1 раз
    ('<div style="font-size:32px;font-weight:800;line-height:1.05;color:#fff;">20 → 20 000+</div>'
     '<div style="font-size:14px;line-height:1.4;margin-top:10px;color:rgba(255,255,255,.75);">визитов/мес из поиска<br>(было ~20 в 2019-м)</div>',
     '<div style="font-size:32px;font-weight:800;line-height:1.05;color:#fff;">×1000</div>'
     '<div style="font-size:14px;line-height:1.4;margin-top:10px;color:rgba(255,255,255,.75);">рост визитов из поиска<br>с 2019 года</div>'),
    ('Начинали с одностраничника, у которого было около 20 визитов в месяц из поиска, — сегодня это полноценный сайт',
     'Начинали с одностраничника, который в поиске почти не находили, — сегодня это полноценный сайт'),
    ('а органика выросла до 20 000+ визитов в месяц.',
     'а визитов из поиска стало примерно в тысячу раз больше.'),
    ('[[$np_ss_case? &name=`np-vinyl` &bg=',
     '[[$np_ss_case? &name=`np-vinyl-calc` &bg='),
]
SECTION = (
    f'<h2 style="{H2}">Органика по Метрике</h2><p style="{P}">'
    'Метрика отдаёт помесячную статистику Vinyl-TM с 2022 года, с него и начинается график. '
    'За единицу взят средний месяц 2022-го. К 2024 году визитов из поиска стало вдвое больше. '
    'В 2025-м был спад, а в 2026-м органика снова пошла вверх: октябрь — ×2,2 к уровню 2022 года.</p>\n'
    '[[$np_ss_case? &name=`np-vinyl-organika` &bg=`#e9ecef` &label=`Визиты Vinyl-TM из поиска по Метрике, индекс к 2022 году: ×2,2 в октябре 2026`]]\n'
)
ANCHOR = '<h2 style="' + H2 + '">Раздел «Марки»: страницы по одному эталону</h2>'

NP = [
    ("{set $ss = ['n' => 'np-vinyl', 'bg' => '#e9ecef', 'l' => 'Калькулятор стоимости оклейки на сайте Vinyl-TM и рост визитов из поиска', 'alt' => 'np-vinyl-marki,np-vinyl-goroda,np-vinyl-raboty']}",
     "{set $ss = ['n' => 'np-vinyl-calc', 'bg' => '#e9ecef', 'l' => 'Калькулятор стоимости оклейки на сайте Vinyl-TM и рост визитов из поиска', 'alt' => 'np-vinyl-organika,np-vinyl-marki,np-vinyl-goroda,np-vinyl-raboty']}"),
]

data = {'r': R, 'section': SECTION, 'anchor': ANCHOR, 'np': NP}
here = Path(__file__).parent
tpl = (here / 'apply.tpl.php').read_text(encoding='utf-8')
tpl = tpl.replace('@@DATA@@', base64.b64encode(json.dumps(data, ensure_ascii=False).encode()).decode())
(here / 'apply.php').write_text(tpl, encoding='utf-8', newline='\n')
(here / 'section.html').write_text(SECTION, encoding='utf-8', newline='\n')
print('ok', len(tpl))
