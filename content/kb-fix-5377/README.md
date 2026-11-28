# #5377 — исправления по аудиту kb #5182 (28.11.2026)

Сайт https://ne-prosto.ru/ (MODX 2.8.8, Timeweb vh306). Выкатка — MODX API по SSH (`ssh redegun@vh306.timeweb.ru "NP_APPLY=1 /opt/php83/bin/php" < apply.php`), guard по SHA каждого элемента, без файлов в webroot (кроме favicon и robots.txt — это и есть правка). `apply.tpl.php` — скрипт без base64 favicon (картинки лежат в `favicon/`).

## Что исправлено (ID kb → URL → было → стало)

| ID | URL | Было | Стало |
|---|---|---|---|
| TECH-10 | все 97 страниц обхода, напр. https://ne-prosto.ru/ , /uslugi/sajtyi , /blog/semanticheskoe-yadro-sajta | `rel=canonical` нет нигде | один `<link rel="canonical">` на адрес ресурса (чанки head и head_2019, тот же вызов, что у og:url) |
| TECH-5 (часть) | /index.php, /KOORDINATYI, /uslugi/sajtyi?utm_source=test, /blog/?page=2 | дубли 200 без canonical | canonical → /, /koordinatyi, /uslugi/sajtyi, /blog/. 301 и Clean-param не делали (склейка вне задачи) |
| TECH-7 | https://ne-prosto.ru/sitemap.xml, /robots.txt | главной нет в карте (ресурс 1 скрыт из меню, pdoSitemap без showHidden); в robots.txt нет Sitemap | главная в карте (90 → 91 URL, остальной состав тот же: исключены 6, 17, 27, 29, 60, 113, 114, которые и раньше не выводились); `Sitemap: https://ne-prosto.ru/sitemap.xml` |
| SEO-TECH-323 | https://ne-prosto.ru/404 | 200, `max-image-preview:large` (индексируемая) | `noindex, nofollow` галочкой TV noindex у ресурса 17 (правило памяти сайта); несуществующие URL — 404 + noindex. Доска #2163 закрыта |
| SEO-TECH-351 | /favicon.ico, все страницы | 404, `rel=icon` нет | favicon.ico (16/32/48), favicon.svg, favicon-192.png, apple-touch-icon.png (180) — 200; 4 ссылки в head. Знак — буква «Н» из логотипа, белая на графитовом квадрате. **Входит в пакет «favicon» сводной страницы** |
| IMGALT-3 (часть) | обложки статей /blog/* (img.article__img), карточки статей на /blog/ и главной, «Ещё интересное» и «Другие услуги», иллюстрации 7 услуг | `alt=''` / `alt=""` | alt = заголовок статьи; у иллюстраций услуг — «Иллюстрация к услуге «Сайты»» и т.п. Декоративные карточки услуг с текстом (главная, /uslugi/) оставлены с `alt=""` — по правилу для декора |
| SEO-ONP-344, CONV-TRUST-200, SEO-CONT-339 (часть) | https://ne-prosto.ru/kompaniya/klientyi/ | 3 из 6 отзывов — рыба: пересказ фильма у «Ирины Павловны Бочковой» (рес. 37), FM-модулятор у «Аршина» (39), «Новый отзыв нового клиента» (70) | TV opinion у 37, 39, 70 очищен — карточки не выводятся (фильтр `opinion!==`); остались 3 настоящих отзыва. Доска #5260 — остальное |

## Не исправлено (важное) и почему
- TECH-2, SEO-ONP-316 — структурированных данных нет совсем (это не битая разметка); пакет JSON-LD на сводной странице ждёт выбора Антона.
- TITLE-3/5, TEXT-1/2/5, SEO-ONP-350, PTYPE-1, SEO-CONT-001 — переписывание title/H1/description и текстов услуг.
- PTYPE-8, SEO-TECH-336, LINK-E3, SEO-CONT-354 — пустые профили, страницы клиентов, вакансии: лечение — noindex/снятие с публикации (закрытие страниц вне задачи). Ресурс 70 «Новый клиент» остался опубликован (снятие — закрытие страницы).
- TECH-5: 301 /index.php → / и Clean-param — склейка вне задачи; canonical уже указывает главную.
- SEO-CONT-369 — состав команды на /kompaniya/ и «В ролях» расходится с профилями, «9 лет» против «© 2007»; опечатки «Пвл Мельник», «Графическая дизайнер» в том же устаревшем блоке (шаблон 7 и чанк np_team). Состав и имя решает Антон/Лена, имя не угадывали.
- CONV-CTA-140, AG-VER-140, CONV-CTA-300 — новая кнопка в шапке, новые цели, новый текст у форм: не ошибка, а доработка/дизайн.
- SEO-TECH-012, SEO-TECH-014 — оптимизация скорости, не ошибка.
- SEO-TECH-013 — спорный пункт верификатора #5182, не трогали.
- Телефон +7 903 в zoon/cityorg/2sp.me — внешние справочники, не сайт.

## Проверка
- `crawl.py` → `crawl-after.json`: sitemap 91 URL + 7 доп. адресов; 97×200, 1×404; у каждой 200-страницы ровно 1 canonical, 4 ссылки icon, 1 H1, необработанных тегов MODX нет; canonical ≠ URL только у дублей (/index.php → /, /KOORDINATYI → /koordinatyi); пустых alt у обложек статей 0; у карточек с пустым alt остались только декоративные карточки услуг (главная, /uslugi/) и фото автора отзыва.
- Скрины 390/1440: `reports/kb-fix-5377/shots/`.
- Формы не трогали и не отправляли.

## Бэкап и откат
- Хостинг: `~/ne-prosto/_agent_archives/task5377/` (before.json — все прежние значения элементов и TV, `*.before.txt`, `robots.txt.before`, after.json — SHA после).
- Копия здесь: `backup/`.
- Откат: вернуть поля элементов из `backup/*.before.txt` (guard по SHA из after.json), TV — из before.json (`tvs`), robots.txt — из `robots.txt.before`; favicon-файлы удалить по точным именам; `cacheManager->refresh()`.
- Исходники `design/20261018/{chunks/head,head_2019,np_article,np_related,templates/8}.html` и `cms-manifest.json` сведены с живыми значениями (templates/8.html в репо отставал от живого ещё до задачи: CTA статей и версии article.css/js).
