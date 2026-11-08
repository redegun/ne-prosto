# Живые обложки Stageshow на проде (#1726, 08.11.2026)

Продолжение #1720 (ролики и предпросмотр). Публикация без Лены — уточнение 3 Антона к #1720.

## Что где
- Ролики и постеры: `/assets/neprosto/stageshow/np-{vinyl,kppf,merci}/` (выложил #1720).
- Стили/скрипт: `/assets/neprosto/stageshow/stageshow.{css,js}?v=1`, подключены в чанках `head` и `head_2019` сразу после site.js (исходники `design/20261018/assets/stageshow/`). На хостинг кладутся отдельно: publish_ci.py их не выкатывает.
- Карточки (листинг /portfolio/ и главная, где есть vinyl-tm): чанк `np_project`, ветка Fenom по `$uri`. Для трёх кейсов вместо `<img>` выводится `<video>` 4:3 (preload=none), остальные карточки не изменились.
- Страницы кейсов 83/84/85: первая строка content `[[$np_ss_case? &name=`np-…` &bg=`…` &label=`…`]]`. Чанк `np_ss_case` выводит широкий ролик 4:3 (до 960px), ниже 768px вертикальный 716×1120.
- JS: IntersectionObserver (rootMargin 200px) подставляет src и запускает ролик, вне экрана ставит на паузу. При prefers-reduced-motion вместо ролика постер `<img>`.
- **Новый кейс:** добавить ветку `{elseif $uri == …}` в `np_project` и вызов `np_ss_case` в content ресурса (поля name/bg/label).

## Выкатка
`apply.tpl.php` (сборка `build.py`) запускается по SSH `php < apply.php`, без файлов в webroot. До записи проверяет SHA текущих значений и делает пробный рендер np_project через pdoTools. Бэкап `before` и `after.json` с SHA: хостинг `~/ne-prosto/_agent_archives/task1726/`. Манифест `cms-manifest.json` сведён с живыми значениями: np_project, head, head_2019 и новый np_ss_case.

Откат: восстановить `np_project`, `head`, `head_2019` и content 83/84/85 из `*.before.html`, удалить чанк `np_ss_case` и файлы `stageshow.{css,js}`, сбросить кеш.

## Проверка (qa1726.mjs, cls1726.mjs; скрины shots/)
- 200, один H1, без горизонтальной прокрутки. Ролики играют (readyState 4) на /portfolio/ (3), /, vinyl-tm, kppf, merci; на 390 загружаются вертикальные. reduced-motion: 0 видео, 1 постер.
- CLS, до → после: 1440: portfolio 0→0, home 0→0, vinyl-tm 0.028→0.041, kppf 0.020→0.001, merci 0.018→0.020. 390: 0.200–0.213 до и после (MAIN сдвигается и без роликов, #1728).
- На vinyl-tm 1440 рост от того же старого сдвига: при подгрузке шрифта H1 перестраивается и подзаголовок поднимается примерно на 100px. Блок с роликом едет вместе с ним, а свой сдвиг не создаёт. Все значения 1440 ниже 0.1.
- Регрессия 14 URL: 200, H1=1, подвал на месте, необработанных тегов нет.
- Предпросмотр `_preview/stageshow-63eca548be8a` перенесён в карантин `~/ne-prosto/_agent_archives/task1726/quarantine/` с MANIFEST, URL отдаёт 404.
