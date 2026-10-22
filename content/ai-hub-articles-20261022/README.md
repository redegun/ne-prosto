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
