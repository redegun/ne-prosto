# Статьи 2–9 хаба «ИИ-ассистент для бизнеса» (#503, 22.10.2026)

Статья 1 — ресурс 104, см. `../ai-hub-article1-20261022/`. Здесь остальные восемь, опубликованы 22.10 в /blog/ («Годнота»), parent 2, template 8, richtext=1.

| № | id | URL | обложка |
|---|---|---|---|
| 4 | 105 | /blog/chat-bot-ili-ii-assistent | ii-hub/chat-bot-ili-assistent.jpg |
| 9 | 106 | /blog/oshibki-vnedreniya-ii-v-biznes | ii-hub/oshibki-vnedreniya.jpg |
| 2 | 107 | /blog/skorost-otveta-na-zayavku | ii-hub/skorost-otveta.jpg |
| 8 | 108 | /blog/kak-poschitat-poteryannye-zayavki | ii-hub/poteryannye-zayavki.jpg |
| 3 | 109 | /blog/vse-obrashheniya-v-odnom-okne | ii-hub/odno-okno.jpg |
| 5 | 110 | /blog/zapisi-zvonkov-dlya-ii-assistenta | ii-hub/zapisi-zvonkov.jpg |
| 7 | 111 | /blog/chto-sprosit-u-klienta-pri-pervom-obrashhenii | ii-hub/chto-sprosit.jpg |
| 6 | 112 | /blog/novyj-ili-postoyannyj-klient | ii-hub/novyj-ili-postoyannyj.jpg |

- Заголовки: для 2, 3, 7, 8, 9 взяты поправленные варианты из README #501 (§2), для 4, 5, 6 — исходные. Ключи — из того же README.
- Перелинковка: каждая статья → /uslugi/ii-assistent-dlya-biznesa (1 раз, анкоры чередуются); 2→1, 8→1, 4→1, 3→6, 6→3+7, 7→6, 5↔9; в статью 1 (104) добавлены ссылки на 2 и 8.
- Страница услуги (103): перед «Частые вопросы» добавлен блок «Полезно почитать» — 9 ссылок абзацами (4, 1, 9 первыми). Список `<ul>` в шаблоне 8 рисуется криво (ul без отступа + a inline-block) — поэтому `<p>`.
- Факты — только со страницы 103 / §4 README #501; цифр нет, кроме явно условного примера расчёта в статье 8. Ласточка/Vinyl-TM не упоминаются.
- humanize-lint: все 8 PASS (`a*.html.humanize.json`), бриф для авторов — BRIEF.md.
- Обложки: Polza без баланса (9 ₽) → `openclaw infer image generate` (gpt-image-2, ~5–10 мин при 8 параллельно), стиль task515/style.txt, промпты prompts.json. 1536×1024 + -768, `public_html/images/godnota/ii-hub/`, TV image + page__image--big (карточка блога, под H1, og:image). Внутри текста иллюстраций нет.
- Проверено 22.10: все 9 URL 200, 1 H1, ссылка на услугу; 1440/390 без горизонтальной прокрутки и JS-ошибок, заглушек noimage в /blog/ нет.

Бэкап: хостинг `~/ne-prosto/_agent_archives/task503/` — parent2-children.before.json, r103.before.html, r103.before-fix.html, r104.before.html, скрипты. Откат: снять с публикации 105–112; content 103/104 вернуть из before-файлов.

## 22.10, #525 — сняты с публикации
Лена не одобряла публикацию. Ресурсы 105–112 переведены в published=0 (resource/unpublish, не удалены). В 104 убраны 2 предложения со ссылками на 107/108, добавленные #503 (текст = r104.before #503). На 103 в «Полезно почитать» оставлена только статья 1. sitemap (pdoSitemap) и «Ещё интересное» (pdoResources) берут только опубликованное — чистятся сами.
Предпросмотр для Лены: статические снимки страниц до снятия, https://ne-prosto.ru/_preview/draft-b05c9e2f0a8cddea/<alias>.html (X-Robots-Tag noindex, плашка «Черновик», ссылки между черновиками ведут на копии). После её одобрения: опубликовать нужные id, вернуть ссылки, удалить эту папку превью (только её, не glob).
Бэкап: хостинг ~/ne-prosto/_agent_archives/task525/ (resources.before.json, r103/r104.before.html, apply.php, scan.php).

## 22.10, #528 — ежедневная автопубликация (одобрено Леной)
Время: **04:00 МСК** — по access_log хостинга за 14–22.10 самый тихий час 04–05 (≈38 запросов/ч всего, ≈12 страниц/ч без ботов; пик 14:00 и 17:00). Яндекс.Метрики на сайте нет, счётчика ne-prosto в токене METRIKA_TOKEN нет — смотрели по логам.
Механизм: штатная отложенная публикация MODX — `pub_date` у 105–112 (published=0). Первый запрос после 04:00 запускает `modRequest::checkPublishStatus` → published=1, publishedon=pub_date, кэш ресурсов чистится. sitemap (pdoSitemap), «Ещё интересное» (`[[!pdoResources]]` в template 8) и /blog/ берут только опубликованное — статья появляется там сама.
Порядок (№ хаба 2→9): 23.10 107 skorost-otveta · 24.10 109 odnom-okne · 25.10 105 chat-bot · 26.10 110 zapisi-zvonkov · 27.10 112 novyj-ili-postoyannyj · 28.10 111 chto-sprosit · 29.10 108 poteryannye · 30.10 106 oshibki.
Перелинковка: ссылки на статьи хаба обёрнуты в `<span data-np-pub="ID">` (предложение целиком) / `<div data-np-pub="ID">` (пункт «Полезно почитать» на 103). Плагин MODX `npHubPubLinks` (id 19, OnWebPagePrerender) показывает обёртку, только если ресурс ID опубликован, иначе вырезает. 104 — вернули 2 предложения #503 (→107, →108); 103 — блок из 9 ссылок как в #503; в черновиках обёрнуты 106→110, 109→112, 110→106, 111→112, 112→111, 112→109. Новая ссылка на ещё не вышедшую статью — оборачивать так же.
Страховка: VPS cron `2 1 23-30 10 *` → `autopub-check.sh` (пинок сайта в 04:02 МСК + проверка 200, иначе alert.sh), лог `logs/ne-prosto-autopub.log`.
Превью `_preview/draft-b05c9e2f0a8cddea/` удалить после 30.10 (только эту папку).
Бэкап: хостинг ~/ne-prosto/_agent_archives/task528/ (resources.before.json 103–112, apply.php, plugin.php). Откат: pub_date=0 у 105–112, content 103–112 из resources.before.json, отключить плагин 19; VPS crontab — /tmp/crontab.bak528.
