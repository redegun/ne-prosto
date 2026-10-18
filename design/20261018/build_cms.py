from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parent
if (ROOT/'releases/v1.json').exists():raise SystemExit('Historical v1 generator: later releases must use their own guarded manifest')
snapshot=json.loads((ROOT/'sources/cms-snapshot.json').read_text())
ot={x['id']:x for x in snapshot['templates']};oc={x['name']:x for x in snapshot['chunks']}
templates={};chunks={};resources={}
def clean(s):return re.sub(r'<!--[\s\S]*?-->|\[\[-[\s\S]*?\]\]','',s)
logo=re.search(r'<svg\b[\s\S]*?</svg>',oc['header_2019']['snippet'])[0]
chunks['np_header']='''<a class="np-skip" href="[[~[[*id]]]]#np-main">К содержимому</a>
<header class="np-header"><a class="np-logo" href="/" aria-label="Непросто — главная">'''+logo+'''<span>Студия дизайна</span></a>
<button class="np-menu-toggle" type="button" aria-expanded="false" aria-controls="np-navigation" hidden><span>Меню</span><span aria-hidden="true">+</span></button>
<nav class="np-nav" id="np-navigation" aria-label="Основная навигация"><a href="/portfolio/">Портфолио</a><a href="/uslugi/">Услуги</a><a href="/kompaniya/">Студия</a><a href="/blog/">Годнота</a><a href="/koordinatyi">Контакты</a></nav>
<a class="np-header__cta" href="/koordinatyi#request">Обсудить проект <span aria-hidden="true">↗</span></a></header>'''
chunks['np_footer']='''<footer class="np-footer">
<div class="np-footer__top"><div><p class="np-kicker">Есть задача?</p><h2>Расскажите,<br>что задумали.</h2></div><div class="np-footer__contact"><a href="/koordinatyi#request" class="np-button">Обсудить проект <span aria-hidden="true">↗</span></a><a href="mailto:[[++e-mail]]">[[++e-mail]]</a><a href="tel:[[++phone:replace=` ==`:replace=`-==`]]">[[++phone]]</a></div></div>
<div class="np-footer__bottom"><div><a href="/" class="np-footer__brand">непросто.</a><p>Студия дизайна<br>© 2007–[[yearsActive]]</p></div>
<nav aria-label="Разделы сайта"><a href="/portfolio/">Портфолио</a><a href="/uslugi/">Услуги</a><a href="/kompaniya/">О студии</a><a href="/blog/">Годнота</a></nav>
<nav aria-label="Студия и сотрудничество"><a href="/kompaniya/klientyi/">Клиенты</a><a href="/kompaniya/v-rolyax/">Команда</a><a href="/kompaniya/vakansii/">Вакансии</a><a href="/koordinatyi">Контакты</a></nav>
<div><div class="np-footer__social"><a href="https://vk.com/public61050900" rel="noopener" target="_blank">ВКонтакте ↗</a><a href="https://www.instagram.com/neprosto_design/" rel="noopener" target="_blank">Instagram ↗</a><a href="https://www.facebook.com/byneprosto" rel="noopener" target="_blank">Facebook ↗</a></div><p class="np-footer__note">Копируйте, скачивайте, делитесь и крадите как художник.<br>Не забывайте указывать источник — ne-prosto.ru.</p></div></div></footer>'''
chunks['np_project']='''<article class="np-project"><a class="np-project__image" href="/{$uri}" aria-label="{$pagetitle | htmlent}"><img src="{$_pls['tv.image'] | phpthumbon : 'w=1200&h=900&zc=0&q=85'}" alt="{($longtitle?:$pagetitle) | htmlent}" loading="lazy" decoding="async" width="1200" height="900"><span class="np-project__arrow" aria-hidden="true">↗</span></a><div class="np-project__caption"><h2><a href="/{$uri}">{$pagetitle | htmlent}</a></h2><p>{$introtext | notags}</p></div></article>'''
chunks['np_article']='''<article class="np-article-card"><a class="np-article-card__image" href="/{$uri}"><img src="{$_pls['tv.image'] | phpthumbon : 'w=900&h=650&zc=1&q=85'}" alt="" loading="lazy" decoding="async" width="900" height="650"></a><div><p class="np-kicker">Дизайн и практика</p><h2><a href="/{$uri}">{$pagetitle | htmlent}</a></h2><p>{$introtext | notags}</p></div></article>'''
chunks['np_services']='''<div class="np-services">
<a class="np-service" href="/uslugi/logotipyi-firmennyie-stili" id="identity"><span class="np-service__number">01</span><h2>Логотипы<br>и фирменные стили</h2><p>Создаём узнаваемый образ компании — от знака и типографики до оформления носителей.</p><span class="np-service__arrow" aria-hidden="true">↗</span></a>
<a class="np-service" href="/uslugi/sajtyi" id="web"><span class="np-service__number">02</span><h2>Сайты<br>и лендинги</h2><p>Проектируем структуру, делаем дизайн, разрабатываем и наполняем сайт.</p><span class="np-service__arrow" aria-hidden="true">↗</span></a>
<a class="np-service" href="/koordinatyi#request" id="upakovka"><span class="np-service__number">03</span><h2>Упаковка</h2><p>Разрабатываем оформление, которое раскрывает характер продукта и помогает заметить его на полке.</p><span class="np-service__arrow" aria-hidden="true">↗</span></a>
<a class="np-service" href="/uslugi/reklamnyie-kampanii" id="advertising"><span class="np-service__number">04</span><h2>Рекламные<br>кампании</h2><p>Придумываем, как рассказать о продукте, акции или событии, и готовим рекламные материалы.</p><span class="np-service__arrow" aria-hidden="true">↗</span></a></div>'''
chunks['np_support']='''<section class="np-support" id="support"><div><p class="np-kicker">После запуска</p><h2>Сайт продолжает<br>развиваться.</h2></div><div><p>Помогаем с наполнением, поддержкой и продвижением. Добавляем страницы и материалы, следим за работой сайта.</p><div class="np-support__links"><a href="/podderzhka/prodvizhenie">Продвижение ↗</a><a href="/podderzhka/podderzhka">Поддержка ↗</a><a href="/podderzhka/soczseti">Соцсети ↗</a></div></div></section>'''
chunks['np_feature']='''<article class="np-feature"><a class="np-feature__image" href="/portfolio/poezd-stankin" aria-label="Дизайн поезда СТАНКИН — открыть кейс"><picture><source type="image/webp" srcset="/images/portfolio/stankin/hero-train-960.webp 960w, /images/portfolio/stankin/hero-train-1920.webp 1920w" sizes="100vw"><img src="/images/portfolio/stankin/photo-31.jpg" width="1920" height="1280" alt="Готовый поезд СТАНКИН с оформлением студии Непросто" fetchpriority="high" decoding="async"></picture><span class="np-feature__open">Смотреть проект <span aria-hidden="true">↗</span></span></a>
<div class="np-feature__caption np-wrap"><div><p class="np-kicker">Транспортный дизайн / 2026</p><h2><a href="/portfolio/poezd-stankin">Поезд СТАНКИН <span aria-hidden="true">↗</span></a></h2></div><p>Концепция и оформление восьми вагонов метро.<br>От полной 3D-модели до готового поезда.</p></div>
<p class="np-feature__credit np-wrap">Фото: <a href="https://80l1ng22vqr6.wfolio.pro/disk/31-08-2026-tematicheskiy-poezd-stankin-nauka-tehnologii-buduschee-xm24cw" target="_blank" rel="noopener">ГЦК</a> / Георгий Васильков</p></article>'''
def shell(body,classes):
 return '<!DOCTYPE html><html lang="ru" prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb#">\n[[$head_2019]]\n<body class="np-site '+classes+'">\n[[$np_header]]\n<main id="np-main">'+body+'</main>\n[[$np_footer]]\n[[$scripts_2019]]\n</body></html>'
templates[5]=shell('''<section class="np-home-hero np-wrap"><div class="np-home-hero__meta"><p class="np-kicker">Непросто — студия дизайна</p><p class="np-kicker">Работаем с 2007 года</p></div><div class="np-home-hero__heading"><h1>Всё гениальное<br><span>непросто.</span></h1><div><p>Фирменные стили, сайты,<br>упаковка и рекламные кампании.<br>От идеи до воплощения.</p><a class="np-text-link" href="/#works">Посмотреть работы <span aria-hidden="true">↓</span></a></div></div></section>
<section class="np-home-work" id="works"><div class="np-section-head np-wrap"><p class="np-kicker">Избранные проекты</p><a class="np-text-link" href="/portfolio/">Все работы <span aria-hidden="true">↗</span></a></div>[[$np_feature]]
<div class="np-project-grid np-wrap np-project-grid--home">[[!pdoResources? &parents=`23` &resources=`-100` &sortby=`menuindex` &sortdir=`ASC` &includeTVs=`image` &limit=`7` &tpl=`np_project`]]</div></section>
<section class="np-wrap np-home-services"><div class="np-section-head"><div><p class="np-kicker">Что мы делаем</p><h2>Дизайн в разных<br>формах.</h2></div><a class="np-text-link" href="/uslugi/">Все услуги ↗</a></div>[[$np_services]][[$np_support]]</section>
<section class="np-home-studio np-wrap"><p class="np-kicker">О студии</p><div><h2>Хорошие проекты<br>делаются вместе.</h2><p>Мы придумываем, рисуем и разрабатываем. Собираем вокруг задачи дизайнеров, иллюстраторов и разработчиков — и остаёмся рядом после запуска.</p><a class="np-text-link" href="/kompaniya/">Познакомиться со студией ↗</a></div></section>
<section class="np-home-journal np-wrap"><div class="np-section-head"><div><p class="np-kicker">Годнота</p><h2>Полезное<br>о дизайне.</h2></div><a class="np-text-link" href="/blog/">Все статьи ↗</a></div><div class="np-journal-grid">[[!pdoResources? &parents=`2` &includeTVs=`image` &limit=`3` &where=`{"isfolder":0}` &tpl=`np_article`]]</div></section>[[$request_form]]''','index-page np-template-5')
templates[1]=shell('''<header class="np-page-hero np-wrap"><p class="np-kicker">Работы студии</p><div><h1>Портфолио</h1><p>Разные задачи.<br>Один внимательный подход.</p></div></header><section class="np-portfolio np-wrap"><nav class="np-filters" aria-label="Категории портфолио">
[[!blog__all? &tpl=`menu__tag` &hereTpl=`menu__tag--active` &text=`Все работы` &placeholder=`tag` &target=`23`]]
[[!TaggerGetTagsFromList? &rowTpl=`menu__tag` &hereTpl=`menu__tag--active` &groups=`2` &limit=`all` &target=`23` &tagsList=`[[*displayed_tags]]`]]
</nav><div class="np-project-grid">[[!pdoResources? &parents=`23` &sortby=`menuindex` &sortdir=`ASC` &includeTVs=`image` &limit=`0` &tpl=`np_project` &where=`[[!TaggerGetResourcesWhere? &where=`{"isfolder":0}`]]`]]</div></section>''','portfolio-page np-template-1')
templates[13]=shell('''<header class="np-page-hero np-wrap"><p class="np-kicker">Наш опыт и знания</p><div><h1>Услуги</h1><p>От фирменного знака<br>до большого проекта.</p></div></header><section class="np-wrap np-services-page">[[$np_services]][[$np_support]]</section>''','about-page np-template-13')
templates[9]=shell('''<header class="np-page-hero np-wrap"><p class="np-kicker">Знания, инструменты, наблюдения</p><div><h1>Годнота</h1><p>То, что помогает<br>делать лучше.</p></div></header><section class="np-journal np-wrap"><nav class="np-filters" aria-label="Рубрики статей">
[[!blog__all? &tpl=`menu__tag` &hereTpl=`menu__tag--active` &text=`Все статьи` &placeholder=`tag` &target=`2`]]
[[!TaggerGetTagsFromList? &rowTpl=`menu__tag` &hereTpl=`menu__tag--active` &groups=`3` &limit=`all` &target=`2` &tagsList=`[[*displayed_tags]]`]]
</nav><div class="np-journal-grid">[[!pdoResources? &parents=`2` &includeTVs=`image` &limit=`0` &tpl=`np_article` &where=`[[!TaggerGetResourcesWhere? &where=`{"isfolder":0}`]]`]]</div></section>''','article-page np-template-9')
for id in [6,7,8,10,11,12,15,16]:
 source=clean(ot[id]['content']).replace('[[$header_2019]]','[[$np_header]]').replace('[[$footer_2019]]','[[$np_footer]]\n[[$scripts_2019]]')
 source=re.sub(r'<body class="([^"]*)">',lambda m:'<body class="np-site np-template-'+str(id)+' '+m[1]+'">',source,count=1)
 if id not in [8,15,16]:
  if id==11:source=source.replace('<div class="process-title__text">[[*longtitle:empty=`[[*pagetitle]]`]]</div>','<h1 class="process-title__text">[[*longtitle:empty=`[[*pagetitle]]`]]</h1>')
  else:source=source.replace('<div class="title-main">[[*longtitle:empty=`[[*pagetitle]]`]]</div>','<h1 class="title-main">[[*longtitle:empty=`[[*pagetitle]]`]]</h1>',1).replace('<h2 class="title-main">[[*longtitle:empty=`[[*pagetitle]]`]]</h2>','<h1 class="title-main">[[*longtitle:empty=`[[*pagetitle]]`]]</h1>',1)
 if '<main' in source:source=source.replace('<main ','<main id="np-main" ',1)
 else:source=source.replace('[[$np_header]]','[[$np_header]]\n<main id="np-main">',1).replace('[[$np_footer]]','</main>\n[[$np_footer]]',1)
 if id==10:source=source.replace('[[pdoResources?','[[pdoResources? \n &parents=`10`\n &resources=`-36`',1)
 if id==8:
  source=source.replace('np-template-8 article-page','np-template-8 article-page [[*parent:is=`2`:then=`np-article-page`:else=`np-service-detail`]]')
  source=source.replace('<div class="article-content">','<div class="article-content">[[*parent:ne=`2`:then=`<p class="np-service-intro">[[*introtext]]</p>`]]')
 if id==12:source=source.replace('w=278&h=239&zc=1','w=900&h=650&zc=0&q=85')
 templates[id]=source
source=ot[4]['content'].replace('<body class="page">','<body class="page np-site np-template-4">')
source=re.sub(r'<header class="page__header">[\s\S]*?</header>','[[$np_header]]',source,count=1)
source=source.replace('<div class="page__content">','<main id="np-main" class="page__content">')
source=source.replace('</div>\n        [[$footer]]','</main>\n        [[$np_footer]]\n'+oc['footer']['snippet'].split('</footer>',1)[1])
templates[4]=source
templates[14]=shell('''<header class="np-page-hero np-wrap"><p class="np-kicker"><a href="/portfolio/">← Портфолио</a></p><div><h1>[[*longtitle:empty=`[[*pagetitle]]`]]</h1><p>[[*introtext]]</p></div></header><div class="np-presentation [[*alias]]">[[*content]]</div>''','presentation-page np-template-14')
assets='<link rel="stylesheet" href="/assets/neprosto/design-20261018/site.css?v=1">\n<script defer src="/assets/neprosto/design-20261018/site.js?v=1"></script>\n'
chunks['head_2019']=oc['head_2019']['snippet'].replace('</head>',assets+'</head>')
chunks['head']=oc['head']['snippet']+'\n'+assets
chunks['scripts_2019']='''<script src="assets/portfolio/js/jquery-3.2.0.min.js"></script>[[*id:is=`7`:then=`<script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU"></script><script src="assets/portfolio/js/map.yandex.js"></script>`]]<script src="assets/portfolio/js/script.js"></script>'''
form=oc['request_form']['snippet'].replace('<div class="title-main">Обсудить проект</div>','<p class="np-kicker">Начнём с разговора</p><h2 class="title-main">Обсудить проект</h2>').replace('ведь нужно с чего-то начинать','Расскажите о задаче — мы свяжемся с вами.')
form=form.replace('type="text" name="name"','type="text" name="name" autocomplete="name" aria-label="Ваше имя" required').replace('type="text" name="contact"','type="email" name="contact" autocomplete="email" aria-label="Электронная почта" required').replace('name="message" rows="10"','name="message" rows="5" aria-label="О проекте"')
form=form.replace('name="file[]" multiple="multiple" class="request-form_attachment" name="attachment"','name="attachment" multiple="multiple" class="request-form_attachment"')
form=form.replace('Сообщение отправлено, надейтесь на ответ','Спасибо! Сообщение отправлено. Мы свяжемся с вами.')
for name,label in [('name','Ваше имя'),('contact','Электронная почта'),('message','О проекте')]:
 form=form.replace('name="'+name+'"','id="np-'+name+'" name="'+name+'"')
 form=re.sub(r'(<(?:input|textarea) [^>]*id="np-'+name+r'"[^>]*>)','<label for="np-'+name+'">'+label+'</label>\\1',form)
chunks['request_form']=form
resources[19]='''<section><h2>Сначала — задача</h2><p>Сайт может рассказывать о компании, представлять продукт, принимать заказы или помогать пользоваться сервисом. Начинаем с брифа: разбираем задачу и состав материалов, проектируем структуру и путь посетителя.</p></section><section><h2>Дизайн, разработка, наполнение</h2><p>Продумываем страницы и навигацию, готовим макеты для компьютера и телефона. Затем верстаем и программируем сайт, подключаем необходимые формы, наполняем его текстами и изображениями.</p></section><section><h2>После запуска</h2><p>Сайт развивается вместе с компанией. Помогаем с поддержкой, новыми страницами, контентом и продвижением.</p><p><a href="/portfolio/portfolio-category/sites/">Посмотреть сайты в портфолио ↗</a></p><p><a href="/koordinatyi#request" class="np-button">Обсудить сайт ↗</a></p></section>'''
resources[20]='''<section><h2>Узнаваемый образ компании</h2><p>Логотип и фирменный стиль помогают компании говорить своим визуальным языком. Работаем со знаком, цветом, типографикой и графикой, чтобы отдельные материалы складывались в цельный образ.</p></section><section><h2>От идеи к применению</h2><p>Начинаем с задачи и контекста: что делает компания, к кому обращается и где будет использовать оформление. Разрабатываем визуальное решение и показываем, как оно работает на носителях.</p></section><section><h2>Система для разных задач</h2><p>Фирменный стиль живёт на сайте, в печатных материалах, рекламе и оформлении пространства. Продумываем его с учётом этих применений.</p><p><a href="/portfolio/portfolio-category/logotipyi/">Логотипы и фирменные стили в портфолио ↗</a></p><p><a href="/koordinatyi#request" class="np-button">Обсудить фирменный стиль ↗</a></p></section>'''
resources[22]='''<section><h2>Что рассказываем и кому</h2><p>Помогаем представить продукт, акцию или событие. Начинаем с содержания: определяем главную мысль и продумываем, как выразить её в рекламных материалах.</p></section><section><h2>Одна идея — разные форматы</h2><p>Разрабатываем концепцию и визуальное оформление, адаптируем их к выбранным носителям. Учитываем, где и как человек увидит сообщение.</p><p><a href="/portfolio/">Посмотреть проекты студии ↗</a></p><p><a href="/koordinatyi#request" class="np-button">Обсудить кампанию ↗</a></p></section>'''
for id,title,text in [(11,'Продвижение сайта','Помогаем развивать сайт в поисковых системах: работаем со структурой, страницами и текстами, проверяем доступность контента и следим за позициями и аналитикой.'),(12,'Поддержка сайта','Следим за работой сайта, дополняем его страницами и материалами, помогаем поддерживать содержание в актуальном состоянии.'),(13,'Работа с соцсетями','Помогаем с оформлением и содержанием страниц в соцсетях. Готовим графические материалы и поддерживаем единый образ компании в разных форматах.')]:
 resources[id]='<section><h2>'+title+'</h2><p>'+text+'</p><p>Объём работ определяем по задаче и текущему состоянию проекта.</p><p><a class="np-button" href="/koordinatyi#request">Обсудить задачу ↗</a></p></section>'

# Complete the family adapters before freezing source hashes.
templates[5]=templates[5].replace('&resources=`-100`','&resources=`101,92,41,62,83,64,91`').replace('&sortdir=`ASC`','&sortdir=`DESC`')
templates[1]=templates[1].replace('&sortdir=`ASC`','&sortdir=`DESC`')
templates[9]=templates[9].replace('np-journal-grid','np-article-grid')
chunks['head']='<meta charset="utf-8">\n'+chunks['head']
chunks['np_team']=templates[7].split('<div class="about-team">',1)[1].split('<div class="about-content">',1)[0]
chunks['np_team']='<div class="about-team">'+chunks['np_team']
legacy="""[[*id:is=`29`:then=`[[$page__heading]]<div class="np-legacy-team">[[$np_team]]</div>`:else=`[[*id:is=`14`:then=`[[$page__heading]]<ol class="jobs">[[!pdoResources? &parents=`14` &resources=`-56` &includeTVs=`requirements` &includeContent=`1` &tpl=`jobs__item` &totalVar=`jobs_total` &limit=`0`]]</ol>`:else=`[[*id:is=`56`:then=`[[$page__heading]]<p class="page__text">Уточните задачи и условия работы у команды студии.</p><a href="/koordinatyi#request" class="np-button">Связаться со студией ↗</a>`:else=`[[content]]`]]`]]`]]"""
templates[4]=templates[4].replace('[[content]]',legacy)

changes=[];sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
def save(kind,id,name,field,content,old,folder):
 path=folder+'/'+str(name)+'.html';(ROOT/folder).mkdir(exist_ok=True);target=('\n'.join(line.rstrip() for line in content.strip().splitlines())+'\n') if content.strip() else '';(ROOT/path).write_text(target)
 changes.append({'type':kind,'id':id,'name':str(name) if kind=='modChunk' else None,'field':field,'path':path,'expected':sha(old) if old is not None else None,'target':sha(target)})
for id,s in templates.items():save('modTemplate',id,id,'content',s,ot[id]['content'],'templates')
for name,s in chunks.items():
 old=oc.get(name);save('modChunk',old['id'] if old else None,name,'snippet',s,old['snippet'] if old else None,'chunks')
for id,s in resources.items():
 old=next(x for x in snapshot['resources'] if x['id']==id);save('modResource',id,id,'content',s,old['content'],'resources')
tv=next(x for x in snapshot['tv_values'] if x['contentid']==36 and x['tmplvarid']==15)
# Retain original in snapshot; do not present a demonstration paragraph as a review.
save('modTemplateVarResource',tv['id'],tv['id'],'value','',tv['value'],'tv-values')
(ROOT/'cms-manifest.json').write_text(json.dumps({'site':'https://ne-prosto.ru/','release':'design-20261018-v1','changes':changes},ensure_ascii=False,indent=2)+'\n')
print('Generated',len(templates),'templates',len(chunks),'chunks',len(resources),'service updates')
