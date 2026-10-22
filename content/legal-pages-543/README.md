# ne-prosto.ru — политика, согласие и галочка во всех формах (#543)

Статус: ОПУБЛИКОВАНО 22.10.2026. **С #547 (22.10): тексты — свои (черновики этапа 1 #543), с pe4a только реквизиты ИП Ветрова; почта везде info@ne-prosto.ru.** Версия «по образцу pe4a» (#543) — в бэкапе task547/before/.

## Страницы
- /politika-konfidencialnosti — ресурс 113, текст policy.html (по образцу https://pe4a.ru/o-kompanii/politika-ip-vetrov-a.a.-v-otnoshenii-obrabotki-personalnyix-dannyix/, адаптирован: формы ne-prosto, вакансии, без Метрики — на сайте её нет).
- /soglasie-na-obrabotku-personalnyh-dannyh — ресурс 114, consent.html (на pe4a отдельного согласия нет — написано в той же логике).
- Оператор ИП Ветров А.А., ИНН 502411688510 (сверен с Эльбой GET /organizations), ОГРНИП и адрес — как на pe4a; e-mail для запросов da@pe4a.ru (как на pe4a, домен на Timeweb, не Gmail — трансграничный пункт не нужен). Телефон — сайта ne-prosto.
- Шаблон 19 «Документ» (template-doc.html): шапка, крошки, H1, текст, подвал. hidemenu=1, searchable=1.

## Формы (все три вида)
- «Обсудить проект» (чанк request_form 93; главная, /koordinatyi, /uslugi/ii-assistent-dlya-biznesa): звёздочки у «Ваше имя»/«Электронная почта», галочка + «* обязательные поля» между файлом и кнопкой (grid-area frmConsent в site.css).
- CTA в статьях (чанк np_cta_form 106 + сниппет npArticleCta 98): статья 104 и черновики 105–112 (превью пересобрано).
- Отклик на вакансию (form--job 42 + jobs__item 40): звёздочки в плейсхолдерах (имя, почта, о себе — там message обязателен и раньше).
- Галочка: `<input type=hidden name=policy value="">` + checkbox required — браузер не даёт отправить; FormIt `policy:required` — сервер отклоняет («отметьте согласие…»). Без hidden FormIt отсутствующее поле НЕ проверяет — не убирать.
- Подвал np_footer (98): .np-footer__legal — две ссылки под «Копируйте…».
- Версии: site.css?v=11 (чанки 11, 89), article.css?v=9 (template 8). CSS — блоки `task 543` в конце site.css/article.css.

## Проверка 22.10 (check.py, Playwright 1440 + 390)
Все формы: без галочки checkValidity=false; с обходом браузера сервер отвечает ошибкой согласия; с галочкой — успех (тест «Тест #543 / тест, не отвечать» из «Обсудить проект» и CTA статьи 104). До исправления hidden-поля 3 тестовых письма ушли без галочки (те же пометки). Без горизонтальной прокрутки и JS-ошибок; 200 и подвал на /, /blog/, /uslugi/, /portfolio/, /kompaniya/, статьях.

## Бэкап и откат
Хостинг ~/ne-prosto/_agent_archives/task543/: before/ (чанки 11,40,42,89,93,98,106, сниппет 98, template 8, site.css, article.css), site.before-fix2.css, before-preview.tgz (старые превью). Откат: вернуть чанки/сниппет/шаблон из before/, css из before/, снять с публикации ресурсы 113/114, сбросить кеш.

## Заметка Антону
Подать уведомление в реестр операторов ПДн Роскомнадзора (если ИП Ветров ещё не в реестре — одно на все сайты). Заявки ne-prosto по-прежнему приходят на Gmail (redegun@gmail.com + 7232308@gmail.com) — в политике, как на pe4a, пункт о локализации в РФ; если нужна полная чистота — перевести приём на почту домена.

## #547 (22.10): свои тексты и почта info@ne-prosto.ru
- 113/114: policy.html/consent.html (apply.php) — черновики этапа 1 #543 + реквизиты ИП Ветрова (ИНН 502411688510, ОГРНИП 309502407100023, адрес Нахабино как на pe4a); e-mail info@ne-prosto.ru, срок хранения 3 года, трансграничного пункта нет (MX Timeweb), веб-аналитики нет (Метрики на сайте нет), Яндекс Карта на /koordinatyi упомянута в cookies. Редакция от 22.10.2026.
- Почта (mail.php): системная настройка `e-mail` = info@ne-prosto.ru (подвал np_footer, шаблон 6 Контакты, request_form); emailTo = `info@ne-prosto.ru` в чанках 26 contacts, 40 jobs__item (раньше ещё taknaprimer@yandex.ru), 93 request_form, шаблоне 3 и сниппете npArticleCta 98; видимый 7232308@gmail.com в чанке 26 и шаблоне 3 заменён. Статические превью _preview/draft-b05c9e2f0a8cddea — тоже. Gmail на сайте не осталось.
- Ящик info@ne-prosto.ru на Timeweb есть (RCPT TO mx1.timeweb.ru → 250, несуществующий → 550). Тест 22.10 ~22:55 МСК: «Тест #547 почта info@» из «Обсудить проект» (/koordinatyi), CTA статьи 104 и вакансии — FormIt success. Доступа к ящику у агентов нет — получение подтверждает человек.
- Бэкап: хостинг ~/ne-prosto/_agent_archives/task547/: before/res113.json, res114.json (версия pe4a), before-mail/ (чанки, шаблон, сниппет, настройка e-mail), before-preview.tgz. Откат почты: вернуть тексты из before-mail/, настройку e-mail из setting-e-mail.txt, сбросить кеш.
