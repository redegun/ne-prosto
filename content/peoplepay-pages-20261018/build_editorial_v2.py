from pathlib import Path
import json,hashlib,copy,requests
from bs4 import BeautifulSoup as B
P=Path(__file__).resolve().parent;A='/images/godnota/peoplepay-pages-20261018/';U='/blog/peoplepay-kakie-stranicy-prinosyat-obrashcheniya';D=P/'preview'/A.lstrip('/')
old=json.loads((P/('payload-v1.json' if (P/'payload-v1.json').exists() else 'payload.json')).read_text());source=B(old['content'],'html.parser');article=source.select_one('.np-pp-article')
if not article:raise RuntimeError('Build v2 once from the first publication source')
original=copy.deepcopy(old);(P/'payload-v1.json').write_text(json.dumps(original,ensure_ascii=False,indent=2))
if article.select_one('.np-pp-byline'):article.select_one('.np-pp-byline').decompose()
lead='Как распределяются обращения между главной, блогом и страницами карт. Разбираем 90 дней статистики People Pay и наши доработки сайта.'
hero=next(f for f in article.select('figure') if '03-home-quiz' in str(f));hero.extract();hero['class']=['np-pp-figure','np-pp-hero-image'];hero.img['loading']='eager';hero.img['fetchpriority']='high';hero.img['sizes']='(max-width: 800px) 92vw, 1280px'
for a in article.select('h2'):
 a['id']='section-'+str(len(a.find_previous_siblings('h2'))+1)
headings=article.select('h2')
# Stable ordinal IDs irrespective of mixed content.
for i,h in enumerate(headings,1):h['id']='section-'+str(i)
names=['Главная','Блог','Страны и карты','Услуги'];visits=[1901,39554,4211,1099];goals=[132,83,77,22];rates=[6.94,.21,1.83,2.00]
def number(x):return f'{x:,}'.replace(',',' ')
fig=next(f for f in article.select('figure') if '01-traffic' in str(f))
rows=''
for name,v,g in zip(names,visits,goals):
 rows+=f'<div class="pp-data-row"><div class="pp-data-name">{name}</div><div class="pp-data-metric"><span>{number(v)}</span><div class="pp-bar-track"><i style="width:{v/39554*100:.3f}%"></i></div></div><div class="pp-data-metric pp-data-goal"><span>{g}</span><div class="pp-bar-track"><i style="width:{g/132*100:.3f}%"></i></div></div></div>'
fig.clear();fig.append(B('<div class="pp-data-chart"><div class="pp-data-head"><span>Страница входа</span><span>Визиты из поиска</span><span>Целевые визиты</span></div>'+rows+'</div><figcaption>Поисковые визиты и визиты с автоцелью формы за 90 дней. Шкалы двух столбцов различаются. <a href="'+A+'01-traffic-and-goals.png" target="_blank" rel="noopener">Открыть график PNG ↗</a></figcaption>','html.parser'))
fig=next(f for f in article.select('figure') if '02-goal' in str(f));rows=''
for name,v in zip(names,rates):
 rows+=f'<div class="pp-rate-row"><span>{name}</span><div class="pp-rate-track"><i style="width:{v/8*100:.3f}%"></i></div><strong>{str(f"{v:.2f}").replace(".",",")}%</strong></div>'
fig.clear();fig.append(B('<div class="pp-rate-chart">'+rows+'</div><figcaption>Доля целевых визитов по страницам входа. Целевой визит — визит с автоцелью формы. <a href="'+A+'02-goal-visit-rate.png" target="_blank" rel="noopener">Открыть график PNG ↗</a></figcaption>','html.parser'))
article['class']=['pp-prose']
links=''.join(f'<a href="{U}#{h["id"]}" data-section="{h["id"]}">{h.get_text()}</a>' for h in headings)
herohead=B('<header class="pp-hero"><p class="pp-eyebrow"><a href="/blog/">Годнота</a><span> / </span>Разбор проекта</p><h1>'+old['pagetitle']+'</h1><p class="pp-lead"></p><div class="pp-meta"><span>Автор: <strong>Антон Ветров</strong></span><span>18 октября 2026 · Данные за 20 июля — 17 октября</span></div></header>','html.parser');herohead.select_one('.pp-lead').string=lead
layout=B('<div class="pp-shell"></div>','html.parser');shell=layout.div;shell.append(herohead);shell.append(hero)
grid=B('<div class="pp-reading-grid"><aside class="pp-toc"><details open><summary>В этой статье</summary><nav aria-label="Содержание статьи">'+links+'</nav></details></aside><div class="pp-reading-slot"></div><aside class="pp-context"><div class="pp-context-card"><p class="pp-eyebrow">О разборе</p><h2>People Pay</h2><p>Каталог, формы, статьи и внутренние ссылки: как мы развиваем сайт и проверяем результат.</p><dl><div><dt>Период</dt><dd>90 полных дней</dd></div><div><dt>Источник</dt><dd>Яндекс.Метрика</dd></div></dl><a href="https://people-pay.ru/" target="_blank" rel="noopener">Сайт проекта ↗</a></div></aside></div>','html.parser');grid.select_one('.pp-reading-slot').replace_with(article);shell.append(grid)
body=str(shell);(P/'content.html').write_text(body);old['content']=body;(P/'payload.json').write_text(json.dumps(old,ensure_ascii=False,indent=2))
template='''<!DOCTYPE html><html lang="ru" prefix="og: http://ogp.me/ns#"><!-- People Pay editorial article -->[[$head_2019]]<body class="np-site np-pp-page"><link rel="stylesheet" href="/images/godnota/peoplepay-pages-20261018/editorial-v2.css?v=2">[[$np_header]]<main id="np-main">[[*content]]</main>[[$np_footer]][[$scripts_2019]]<script defer src="/images/godnota/peoplepay-pages-20261018/editorial-v2.js?v=2"></script></body></html>'''
(P/'template-v2.html').write_text(template)
# Preview from the current live shell, with article-only layout.
r=requests.get('https://ne-prosto.ru'+U,timeout=40);r.raise_for_status();s=B(r.text,'html.parser');s.body['class']=['np-site','np-pp-page']
main=s.select_one('main');main.clear();main.append(B(body,'html.parser'))
for el in list(s.select('script')):el.decompose()
if s.base:s.base.decompose()
s.head.append(s.new_tag('link',rel='stylesheet',href=A+'editorial-v2.css?v=2'));s.head.append(s.new_tag('meta',attrs={'name':'robots','content':'noindex,nofollow'}));s.body.append(s.new_tag('script',defer='',src='/assets/neprosto/design-20261018/site.js?v=6'));s.body.append(s.new_tag('script',defer='',src=A+'editorial-v2.js?v=2'))
(P/'preview/index.html').write_text(str(s))
release={'resource':102,'source_template':8,'template_name':'People Pay editorial article 20261018','expected_content_sha':hashlib.sha256(original['content'].encode()).hexdigest(),'target_content_sha':hashlib.sha256(body.encode()).hexdigest(),'target_template_sha':hashlib.sha256(template.encode()).hexdigest()}
(P/'release-v2.json').write_text(json.dumps(release,indent=2));print('Prepared editorial v2: hero, TOC, centered reading column, native responsive charts')
