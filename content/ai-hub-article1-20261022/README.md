# Статья 1 хаба «ИИ-ассистент для бизнеса» (#512)

Живой адрес: https://ne-prosto.ru/blog/kuda-propadayut-zayavki-iz-messendzherov — ресурс MODX **104**, parent 2 (/blog/, «Годнота»), template 8, richtext=1 (как статьи 77–82).

- H1/pagetitle «Куда пропадают заявки из мессенджеров, пока менеджер занят»; TV titl «Куда пропадают заявки из мессенджеров и как не терять клиентов — Непросто»; desc = description.
- Ключи #501 (статья 1): потерянные заявки, потеря заявок, ответы клиентам в мессенджерах, как не терять клиентов, теряются заявки, заявки из мессенджеров, автоответы в мессенджерах, H2 «Как не терять заявки из мессенджеров».
- Ссылка на услугу: «ИИ-ассистент для бизнеса» → /uslugi/ii-assistent-dlya-biznesa (раздел «Где помогает ИИ-ассистент»); CTA → /koordinatyi.
- Факты об ассистенте — только из hub README §4 / страницы 103. Ласточка и Vinyl-TM не упоминаются, цифр нет.
- Перелинковка 1↔8 и 1↔2 не сделана: статей 2 и 8 ещё нет. На странице услуги блок «Полезно почитать» по-прежнему скрыт (ждёт статей 4/1/9).
- Обложка: типографическая, в стиле обложки статьи 102 (Pillow, Segoe UI), public_html/images/godnota/ii-zayavki-messendzhery.jpg 1800×1300; TV image + page__image--big.
- humanize-lint: PASS words=650 labels=0 leaks=0 not_but=0 morals=0 callouts=0 (WARN: нет цифр — намеренно, источников с цифрами нет).

Бэкап: хостинг ~/ne-prosto/_agent_archives/task512/ (parent2-children.before.json, resource.after.json, content.html, create.php). Откат — снять с публикации ресурс 104 и удалить картинку.
Проверка 22.10: 200, 1 H1, title/description, og:image; 1440/390 без горизонтальной прокрутки, JS-ошибок нет; в /blog/ карточка первой.

## Иллюстрации (#515, 22.10)
- Лена не видела картинок (была только типографская обложка). Сгенерированы 4 иллюстрации Polza.ai openai/gpt-image-2.5-flare (1536×1024, стиль: матовый 3D, графит/молочный/лайм, без текста), промпты в task515/.
- Обложка (TV image + page__image--big, og:image, карточка блога) → images/godnota/zayavki-messendzhery/hero.jpg — под H1.
- В тексте 3 <figure class="np-article-figure"> (srcset 768/1200): после 1-го абзаца разделов «Где теряются заявки» (kanaly), «Почему клиент не ждёт» (klient-zhdet), «Где помогает ИИ-ассистент» (assistent).
- Бэкап: хостинг ~/ne-prosto/_agent_archives/task515/ (resource104.before.json, old-cover.jpg, apply.php). Откат: вернуть content и TV из before.json.
- Проверено 1440/390: все 4 картинки грузятся, видимы, без горизонтальной прокрутки и JS-ошибок.
