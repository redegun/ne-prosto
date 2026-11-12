# max-image-preview:large в meta robots (#2148, 13.11.2026)

Зачем: Google Discover и крупные превью в выдаче берут картинку большого размера только при `max-image-preview:large`. На сайте meta robots не было вовсе (кроме noindex-страниц). Из #2138 (картинки ≥1200, сайт их не обрезает); проверка автопилотов — VPS `services/office-seo-worker/img-check.py`.

## Как устроено
- meta robots выводит TV `noindex` (id 2, checkbox «Индексировать страницу», значение «Нет» = `<meta name="robots" content="noindex, nofollow">`), вызов в чанках `head` (template 4, 2) и `head_2019` (все остальные шаблоны страниц).
- Было `[[*noindex]]`, стало `[[*noindex:default=`<meta name="robots" content="max-image-preview:large">`]]`:
  - галочка «Нет» стоит → как раньше, только `noindex, nofollow` (сейчас ресурсы 60 index-new и 61-черновик);
  - галочки нет → `<meta name="robots" content="max-image-preview:large">`.
- Новая статья/страница получает тег сама. Закрыть страницу от индексации — по-прежнему галочка TV noindex.

## Выкатка
`apply.php` по SSH (`ssh redegun@vh306.timeweb.ru /opt/php83/bin/php < apply.php`, применение — `NP_APPLY=1`), без файлов в webroot. Guard: SHA чанков до правки, ровно одно вхождение `[[*noindex]]`, пробный рендер тега на ресурсах 60, 61 (ждём noindex), 1, 122, 14 (ждём max-image-preview). Затем сохранение и `cacheManager->refresh()`.
SHA: head bb6563be… → a36c4484…, head_2019 c48a4a5f… → 6aabe95c… Манифест `design/20261018/cms-manifest.json` и `design/20261018/chunks/head*.html` сведены.

Бэкап: хостинг `~/ne-prosto/_agent_archives/task2148/{head,head_2019}.before.html`, `after.json`.
Откат: вернуть в обоих чанках `[[*noindex]]` (или `snippet` из `*.before.html`), сбросить кеш MODX.

## Проверка
- `robots_scan.py` по всем 89 опубликованным HTML-ресурсам до/после (`before.json`, `after.json`): 88 — `max-image-preview:large`, 1 (index-new) — `noindex, nofollow` как было; коды ответа, число H1 и `</head>` не изменились.
- `img-check.py https://ne-prosto.ru/blog/skorost-zagruzki-sajta` → `IMG_CHECK: PASS`, строки `IMG_SITE` нет.
- Playwright 1440/390 (`shots.py`, `qa.json`): главная, статья, блог, вакансии — 200, H1=1, без горизонтальной прокрутки, битых картинок и ошибок JS нет.
