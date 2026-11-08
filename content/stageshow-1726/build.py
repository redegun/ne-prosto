import hashlib, base64, json
from pathlib import Path
old_np = Path('np_project.old.html').read_text(encoding='utf-8')
assert hashlib.sha256(old_np.encode()).hexdigest() == 'a43cd19b000c4a683e473ca06acef74c724b69bb5bd8d5e80913f8012dca47ff'
CASES = {
    'vinyl-tm': ('np-vinyl', '#e9ecef', 'Калькулятор стоимости оклейки на сайте Vinyl-TM и рост визитов из поиска'),
    'kppf': ('np-kppf', '#0b0a0b', 'Страницы КППФ по городам: выбор города, заявка на плёнку и сайт в выдаче'),
    'merci': ('np-merci', '#dfe8f5', 'Мерсидон: раздел «Пирсинг», оплата через Робокассу и рост визитов из поиска'),
}
M = '/assets/neprosto/stageshow'


def vid(n, tag, w, h, l):
    return (f'<video muted loop playsinline preload="none" width="{w}" height="{h}" data-poster="{M}/{n}/poster-{tag}.png" aria-label="{l}">'
            f'<source data-src="{M}/{n}/{n}-{tag}.webm" type="video/webm"><source data-src="{M}/{n}/{n}-{tag}.mp4" type="video/mp4"></video>')


sets = ''.join(("{if" if i == 0 else "{elseif") + f" $uri == 'portfolio/{s}'}}{{set $ss = ['n' => '{n}', 'bg' => '{bg}', 'l' => '{l}']}}"
               for i, (s, (n, bg, l)) in enumerate(CASES.items())) + '{/if}'
card = ('{set $ss = 0}' + sets +
        '{if $ss?}<span class="np-ss np-ss--card" style="--np-ss-bg:{$ss.bg}"><span class="np-ss__v" style="aspect-ratio:4/3">'
        '<video muted loop playsinline preload="none" width="1440" height="1080" data-poster="' + M + '/{$ss.n}/poster-1440.png" aria-label="{$ss.l}">'
        '<source data-src="' + M + '/{$ss.n}/{$ss.n}-1440.webm" type="video/webm"><source data-src="' + M + '/{$ss.n}/{$ss.n}-1440.mp4" type="video/mp4"></video></span></span>'
        '{else}')
i0 = old_np.index('<img ')
i1 = old_np.index('>', i0) + 1
new_np = old_np[:i0] + card + old_np[i0:i1] + '{/if}' + old_np[i1:]
case = ('<div class="np-ss np-ss--case" style="--np-ss-bg:[[+bg]]">'
        '<div class="np-ss__v np-ss__v--wide" style="aspect-ratio:4/3">' + vid('[[+name]]', '1440', 1440, 1080, '[[+label]]') + '</div>'
        '<div class="np-ss__v np-ss__v--tall" style="aspect-ratio:716/1120">' + vid('[[+name]]', '390', 716, 1120, '[[+label]]') + '</div></div>')
tags = {83: 'vinyl-tm', 84: 'kppf', 85: 'merci'}
calls = {str(i): f'[[$np_ss_case? &name=`{CASES[s][0]}` &bg=`{CASES[s][1]}` &label=`{CASES[s][2]}`]]' for i, s in tags.items()}
link = '\n<link rel="stylesheet" href="/assets/neprosto/stageshow/stageshow.css?v=1">\n<script defer src="/assets/neprosto/stageshow/stageshow.js?v=1"></script>'
Path('np_project.new.html').write_text(new_np, encoding='utf-8', newline='')
Path('np_ss_case.html').write_text(case, encoding='utf-8', newline='')
b = lambda s: base64.b64encode(s.encode() if isinstance(s, str) else s).decode()
tpl = Path('apply.tpl.php').read_text(encoding='utf-8')
for k, v in {'CSS': Path('stageshow.css').read_bytes(), 'JS': Path('stageshow.js').read_bytes(), 'CASE': case,
             'NP': new_np, 'LINK': link, 'CALLS': json.dumps(calls, ensure_ascii=False)}.items():
    tpl = tpl.replace('@@' + k + '@@', b(v))
Path('apply.php').write_text(tpl, encoding='utf-8', newline='\n')
print(new_np)
print('np_project new sha', hashlib.sha256(new_np.encode()).hexdigest())
