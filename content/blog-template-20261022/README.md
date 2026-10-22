# Шаблон статьи блога: обложка, колонка, оглавление (#520, 22.10)

Запрос Лены к #512/#515 по /blog/kuda-propadayut-zayavki-iz-messendzherov: обложка на весь экран, текст сдвинут вправо, нет оглавления.

## Что сделано
- Template 8 общий для статей блога (parent 2, body `np-article-page`) и страниц услуг (`np-service-detail`). Правка только для parent 2: в шаблон добавлены две строки `[[*parent:is=`2`:then=...]]` — `article.css?v=2` сразу после `<body>` и `article.js?v=2` (defer) перед `</body>`. Общий site.css/site.js не трогали, услуги не затронуты.
- Файлы: public_html/assets/neprosto/design-20261018/article.{css,js}; копии в design/20261018/assets/.
- Desktop ≥1101px: `.article-wrapper` — сетка 780px текст + 220–280px оглавление; H1 и «Ещё интересное» на всю ширину. Обложка `.article__img` = ширине текста (780×520 вместо 1325×883), текст от левого края под H1 (было margin-left:auto → x=602). Оглавление справа, sticky, подсветка текущего раздела.
- ≤1100px: оглавление — сворачиваемый блок «Содержание» между обложкой и текстом (закрыт по умолчанию, по клику по пункту закрывается).
- Оглавление строит article.js по H2 внутри `.article-content` (≥2 штук), id — транслит. Ссылки абсолютные (на сайте `<base href="https://ne-prosto.ru/">`, `#id` уводил на главную). Если заголовки уже с номерами («1. …», статьи 81/82) — свои номера 01/02 не показываются.
- Заодно: счётчик просмотров прижат влево под H1; у ol/ul в тексте отступ 1.4em (на 390px номера списка уходили за край).

## Проверка 22.10
1440/1024/390: статьи 104, 81, 82, 78 — обложка 780×520 (моб. 350×233), текст x=58 (моб. 20), оглавление есть, горизонтальной прокрутки нет, JS-ошибок нет; клик по пункту — переход к разделу, подсветка. Услуги /uslugi/ii-assistent-dlya-biznesa, /uslugi/sajtyi, /uslugi/logotipyi-firmennyie-stili — article.css не подключён, вид прежний. Статья 102 (template 18), /blog/, главная, /koordinatyi, /uslugi/ — 200, 1 H1, подвал. Скрины: shots/ (before104-* — до).

## Бэкап и откат
Хостинг ~/ne-prosto/_agent_archives/task520/: template8.before.html (SHA f30958…), template8.after.html (3e6980…), apply.php/bump.php, article.v1.*. Откат: вернуть content template 8 из template8.before.html (SHA guard 3e6980…), сбросить кеш; article.{css,js} можно оставить (без шаблона не подключаются).

## Статья по центру (#527, 22.10, п.4 #523/#524, выбор Лены)
article.css: `.article-wrapper{justify-content:center}` вместо `start` (desktop ≥1101px) — блок H1 + текст 780 + «Содержание» 280 стоит по центру, поля равные: 1920 — 372/372, 1440 — 147/147, 1366 — 112/112. Хлебные крошки вне сетки, остались у левого поля (как на макете A из #524). Текст, картинки, шрифты, мобильный вид не менялись. Версия в template 8: article.css?v=3 (кеш у файла год). Проверка: статьи kuda-propadayut…, besplatnye-kirillicheskie-shrifty, upakovka-kotoraya-prodaet-priemy на 1920/1440/1366/390 — 200, без горизонтальной прокрутки и JS-ошибок; услуга ii-assistent-dlya-biznesa article.css не подключает. Скрины и скрипт: center-527/. Бэкап: хостинг _agent_archives/task527/ (article.before.css, template8.before.html SHA 58659f…). Откат: вернуть article.before.css; версию можно не трогать.

## Оглавление не заезжает на «Ещё интересное» (#529, 22.10, к #527)
Было: `.np-toc` — sticky прямо в сетке `.article-wrapper`, а sticky ограничивается всем контейнером (включая «Ещё интересное»), поэтому в конце статьи оглавление ехало дальше и накрывало карточки (на 1440 до ~1000px). Стало: article.js кладёт `details.np-toc` в обёртку `div.np-toc-rail`; в article.css (≥1101px) обёртка занимает колонку 2, строки 2–4 (`align-self:stretch`, `margin-bottom:90px` = отступ под текстом), и sticky упирается в её низ — оглавление останавливается на конце текста. Мобильный вид (сворачиваемый блок) не менялся. Версии в template 8: article.css?v=4, article.js?v=3.
Проверка toc-529/check.py: 7 статей с оглавлением (короткие servisy-dlya-podbora-cveta, besplatnye-kirillicheskie-shrifty … длинная kuda-propadayut…) × 1920/1440/1366/390 — 200, низ оглавления ≤ низа текста (зазор до «Ещё интересное» 90px), при чтении оглавление липнет, без горизонтальной прокрутки и JS-ошибок; на 390 «Содержание» раскрывается, пункт ведёт к разделу. Скрины toc-529/live-*.png. Бэкап: хостинг _agent_archives/task529/ (article.before.css/js, template8.before.html SHA 33ea6a…, bump.php). Откат: вернуть article.before.css/js и template8.before.html (guard: SHA b7a064…), сбросить кеш.
