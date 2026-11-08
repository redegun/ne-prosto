# Живые обложки Stageshow: lrrazbor, ФЛиС, Муза (#1727, 08.11.2026)

Продолжение #1720/#1726 (инфраструктура: чанк `np_ss_case`, `stageshow.{css,js}`, ветки в `np_project`, см. `content/stageshow-1726/README.md`). Публикация на прод без Лены — уточнение 3 Антона к #1720.

## Что сделано
- Сцены (ПК `D:/project/tut/tools/stageshow-pilot/examples/`): `np-lrrazbor` (поиск «суппорт дискавери 3»: «Ничего не найдено» → «Найдено 53 детали», телефон: тяжёлые запросы 30 с → 0,5 с, 43 000+ запросов, ≈140 правил), `np-flis` (Каталог → мега-меню → «Зимняя спецодежда» → фильтр «Сигнальная», телефон: 92 SEO-описания, перенос на MODX с нуля), `np-muza` (вкладка «Волосы» → «Записаться» → мастер, время 11:30 → «Вы записаны», телефон: 200+ услуг из YClients каждый день, 48 разделов, 16 мастеров). Стиль с живых сайтов: Onest/#212122/#1d6fe8 (lrrazbor.ru), Montserrat/#15181e/#f2641e (firmaflis.ru), Montserrat/#591820/#F8F3EB (salonmuza.ru). Шрифт Onest добавлен в `examples/np-fonts/`.
- Gate: wide, 390 и `--states` — `rehearsal passed` у всех трёх (9 из 9).
- make-loop: петли 7,9 с (lrrazbor), 9,4 с (flis), 10,4 с (muza); файлы 80–300 КБ. На хостинге `/assets/neprosto/stageshow/np-{lrrazbor,flis,muza}/`.
- `np_project`: три ветки `{elseif $uri == …}` (portfolio/lrrazbor-poisk, portfolio/firmaflis, portfolio/muza).
- Контент ресурсов 101 (lrrazbor-poisk, tpl 15) и 92 (firmaflis): первой строкой вызов `np_ss_case`.
- Новый ресурс 119 `/portfolio/muza` (tpl 11, parent 23, menuindex 49, published), по образцу кейса Мерсидон (85): три плашки, абзац, скрин `images/portfolio/clients/muza.jpg`, кнопка на salonmuza.ru; TV image `muza-card.jpg`. Факты — clients/muza (MEMORY, log 2026-10: переезд с Tilda на MODX, синк YClients ежедневно, 48 разделов, 16 мастеров, 200+ услуг, цели Метрики). Тегов Tagger у 85 нет, у 119 тоже.
- Главная: в выборке есть 101 и 92, поэтому их карточки на главной теперь тоже ролики.

## Выкатка
`apply.tpl.php` + `build.py` → `apply.php`, запуск `ssh redegun@vh306.timeweb.ru php < apply.php` (без файлов в webroot), запись только при файле `_agent_archives/task1727/APPLY` = yes (удалён после). Guards: SHA np_project и content 92/101, нет alias muza, все 18 файлов роликов и 2 картинки на месте, пробный рендер pdoTools.

Бэкап: хостинг `~/ne-prosto/_agent_archives/task1727/` (np_project.before.html, res92/res101.content.before.html, after.json, created.json); копии content — здесь.
Откат: вернуть np_project и content 92/101 из before, ресурс 119 снять с публикации или удалить, сбросить кеш.

## Проверка (qa1727.mjs, скрины shots/)
- 200, H1=1, без горизонтальной прокрутки: /portfolio/, /portfolio/lrrazbor-poisk, /portfolio/firmaflis, /portfolio/muza, главная — 1440 и 390.
- Ролики играют (readyState 4, !paused); на 390 на страницах кейсов грузится `-390.webm`. reduced-motion на /portfolio/muza: 0 видео, 1 постер.
- CLS до → после: 1440 везде 0 (firmaflis 0,0065 → 0); 390 ≈0,20 до и после (старый сдвиг MAIN, #1728).
- Range → 206 с верным content-type; /portfolio/muza в sitemap.
