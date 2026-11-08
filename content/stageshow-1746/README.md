# Vinyl-TM: несколько роликов на одном кейсе (#1746, 08.11.2026)

Антон 08.11: «для разнообразия делать разные на одном клиенте». Кроме главного ролика np-vinyl (калькулятор + визиты из поиска, #1720/#1726) — три сцены по другим реальным работам.

## Сцены (ПК `D:/project/tut/tools/stageshow-pilot/examples/`)
- `np-vinyl-marki` — раздел «Марки»: сетка 12 марок, появляются 6 новых (ГАЗ, Fiat, IVECO, Škoda, Sollers, Toyota) с меткой «новая», клик Renault → страница марки (тарифы, калькулятор, кейсы, FAQ). Телефон: «12 + 6». Факты: clients/vinyl-tm/memory/project_vinyl_marki_redesign.md.
- `np-vinyl-goroda` — страницы городов: Москва → Казань, меняется заголовок и примеры работ, 4 тарифа 950/1 300/2 300/7 500 ₽/м². Телефон: 46 городов. Факты: region-branches-index.md, project_vinyl_region_branches.md.
- `np-vinyl-raboty` — каталог работ: вкладка «Фургоны», карточка → модель/тариф/дизайн/оклейка. Телефон: 580+ страниц работ. Факты: reference_vinyl_cases_constructor.md, аудит 581 страницы (#31).
- Общие стили `np-vinyl-marki/vx.css` поверх `np-vinyl/vinyl.css`. Gate wide/390/--states — rehearsal passed 9/9. Петли ≈ 9–11 с, файлы 100–350 КБ.
- Грабля make-loop: если первый бит сцены — `a.set` без движения курсора, петля не находится (кадры второго круга сдвинуты). Лечится движением курсора первым битом.

## На сайте
- Файлы: `/assets/neprosto/stageshow/np-vinyl-{marki,goroda,raboty}/` (webm/mp4 1440 и 390, poster-1440/390).
- Ресурс 83 (/portfolio/vinyl-tm): перед блоком «Над проектом работали» три раздела `<h2>` + абзац + `[[$np_ss_case? &name=`np-vinyl-…`]]` (текст — sections.html). Абзацы встают вправо по правилу дизайна `.np-template-11 .process-wrapper>p` (как все абзацы кейса).
- Карточка vinyl-tm (`np_project`, /portfolio/ и главная): в `$ss` поле `alt`, у `<video>` атрибут `data-ss-alt`. `stageshow.js` v2: случайный ролик на показ, после каждого проигрыша — следующий по кругу (loop снимается только у таких видео); грузится только видимое (IntersectionObserver, preload=none). `head`/`head_2019`: `stageshow.js?v=2` (кеш на год).
- **Стандарт для остальных кейсов:** сцены `np-<slug>-<тема>`, раздел в content кейса + `np_ss_case`, в `np_project` у ветки кейса `'alt' => 'имя1,имя2'`.

## Выкатка
`build.py` → `apply.php`, `ssh redegun@vh306.timeweb.ru php < apply.php` (файлов в webroot нет), запись только при `_agent_archives/task1746/APPLY`=yes (удалён). Guards: одна вхождение старой ветки vinyl и `<video` в np_project, `?v=1` в head-чанках, якорь в content 83, все 18 файлов на месте, пробный рендер pdoTools. cms-manifest и chunks/ сведены с живыми значениями.

Бэкап: хостинг `~/ne-prosto/_agent_archives/task1746/` (np_project/head/head_2019/res83 .before.html, stageshow.js.before, after.json); копия content 83 — `res83.before.html`.
Откат: вернуть чанки и content 83 из before, stageshow.js из stageshow.js.before, сбросить кеш (файлы роликов можно оставить).

## Проверка (qa1746.mjs, rot1746.mjs)
- 200, H1=1, без горизонтальной прокрутки: /portfolio/vinyl-tm, /portfolio/, главная на 1440 и 390.
- /portfolio/vinyl-tm: 4 ролика играют (шапка + 3 раздела), readyState 4; на 390 — `-390.webm`.
- Карточка на /portfolio/ за 40 с прошла по кругу raboty → vinyl → marki → goroda → raboty.
- CLS до → после: vinyl-tm 1440 0,041 → 0,030; 390 0 → 0; /portfolio/ и главная 0 → 0.
- 18 файлов 200 с верным content-type, Range → 206.
