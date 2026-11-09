<?php
/**
 * npCases — блок «Что сделали» на странице кейса и теги+метрика в карточке портфолио (#1882).
 * Данные: ~/ne-prosto/np-cases/<slug портфолио>.json (вне webroot), их выкладывает
 * VPS sites/ne-prosto/cases/publish.py из cases/<client>.yml. Нет файла — пустой вывод.
 * Вызовы: в content кейса [[!npCases]]; в чанке np_project {'npCases' | snippet : ['mode' => 'card', 'uri' => $uri]}
 */
$mode = (string)$modx->getOption('mode', $scriptProperties, 'case');
$uri = (string)$modx->getOption('uri', $scriptProperties, '');
if ($uri === '' && $modx->resource) $uri = (string)$modx->resource->get('uri');
$slug = preg_replace('~[^a-z0-9_-]~', '', strtolower(basename(trim($uri, '/'))));
if ($slug === '') return '';
$file = dirname(rtrim(MODX_BASE_PATH, '/')) . '/np-cases/' . $slug . '.json';
if (!is_file($file)) return '';
$d = json_decode((string)file_get_contents($file), true);
if (!is_array($d) || empty($d['cases'])) return '';
$e = function ($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); };
$css = '/assets/neprosto/cases/cases.css?v=' . (isset($d['css_v']) ? (int)$d['css_v'] : 1);
if ($mode === 'card') {
    // карточка рендерится внутри кешируемого листинга: regClientCSS в кеш не попадает, поэтому <link> один раз в разметке
    $h = '';
    if (!$modx->getPlaceholder('np_did_css')) { $modx->setPlaceholder('np_did_css', 1); $h .= '<link rel="stylesheet" href="' . $css . '">'; }
    $h .= '<div class="np-did-card">';
    if (!empty($d['tags'])) {
        $h .= '<ul class="np-did-card__tags" aria-label="Что делали">';
        foreach (array_slice($d['tags'], 0, 4) as $t) $h .= '<li>' . $e($t) . '</li>';
        $h .= '</ul>';
    }
    if (!empty($d['metric']['value'])) {
        $h .= '<p class="np-did-card__metric"><b>' . $e($d['metric']['value']) . '</b> <span>' . $e($d['metric']['label']) . '</span></p>';
    }
    return $h . '</div>';
}
$modx->regClientCSS($css);

$months = ['01' => 'январь', '02' => 'февраль', '03' => 'март', '04' => 'апрель', '05' => 'май', '06' => 'июнь',
    '07' => 'июль', '08' => 'август', '09' => 'сентябрь', '10' => 'октябрь', '11' => 'ноябрь', '12' => 'декабрь'];
$date = function ($s) use ($months) {
    $s = (string)$s;
    if (preg_match('~^(\d{4})-(\d{2})~', $s, $m) && isset($months[$m[2]])) return $months[$m[2]] . ' ' . $m[1];
    return $s;
};
$items = array_slice(array_values(array_filter($d['cases'], function ($c) { return !isset($c['show']) || $c['show']; })), 0, 8);
$count = [];
foreach ($items as $c) { $t = (string)$c['type']; $count[$t] = isset($count[$t]) ? $count[$t] + 1 : 1; }
$name = isset($d['name']) ? $d['name'] : '';
$h = '<section class="np-did" id="chto-sdelali" aria-labelledby="np-did-h">';
$h .= '<div class="np-did__head"><p class="np-kicker">Что сделали</p><h2 id="np-did-h">Задачи, которые мы решили' . ($name !== '' ? ' для «' . $e($name) . '»' : '') . '</h2>';
$h .= '<ul class="np-did__types">';
foreach ($count as $t => $n) $h .= '<li>' . $e($t) . ' <span>' . (int)$n . '</span></li>';
$h .= '</ul></div><div class="np-did__list">';
foreach ($items as $i => $c) {
    $h .= '<details class="np-did__item" data-type="' . $e($c['type']) . '"' . '>';
    $h .= '<summary><span class="np-did__meta"><span class="np-did__tag">' . $e($c['type']) . '</span><span class="np-did__date">' . $e($date($c['date'])) . '</span></span>';
    $h .= '<span class="np-did__title">' . $e($c['title']) . '</span><span class="np-did__plus" aria-hidden="true"></span></summary>';
    $h .= '<div class="np-did__body"><dl>';
    foreach (['task' => 'Задача', 'done' => 'Что сделали', 'result' => 'Результат'] as $k => $label) {
        if (!empty($c[$k])) $h .= '<div><dt>' . $label . '</dt><dd>' . $e($c[$k]) . '</dd></div>';
    }
    $h .= '</dl>';
    $shots = [];
    foreach (['before' => 'До', 'after' => (empty($c['before']) ? 'Как стало' : 'После')] as $k => $label) {
        if (empty($c[$k]['src'])) continue;
        $im = $c[$k];
        $shots[] = '<figure><img src="' . $e($im['src']) . '" alt="' . $e($c['title'] . ' — ' . mb_strtolower($label, 'UTF-8')) . '" width="' . (int)$im['w'] . '" height="' . (int)$im['h'] . '" loading="lazy" decoding="async"><figcaption>' . $label . '</figcaption></figure>';
    }
    if ($shots) $h .= '<div class="np-did__shots np-did__shots--' . count($shots) . '">' . implode('', $shots) . '</div>';
    $h .= '</div></details>';
}
return $h . '</div></section>';
