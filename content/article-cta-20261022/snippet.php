<?php
// task 538: ненавязчивые призывы в статьях блога (parent 2), вариант 3 Лены.
// &pos=`mid` — блок под тему статьи; плагин npArticleCtaPlace ставит его перед N-м H2 (TV npCtaPlace, по умолчанию 3).
// &pos=`end` — блок по услуге, на которую ссылается статья (чанк np_cta_services), в конце текста перед «Ещё интересное».
// Включено для статей id>=104 (новые); TV npCtaMode: off — выключить, on — включить в старой статье.
$res = $modx->resource;
if (!$res || (int)$res->get('parent') !== 2) return '';
$tv = function ($n) use ($res) { return trim((string)$res->getTVValue($n)); };
$mode = $tv('npCtaMode');
if ($mode === 'off' || ($mode !== 'on' && (int)$res->get('id') < 104)) return '';
$chunk = $modx->getObject('modChunk', ['name' => 'np_cta_services']);
$cfg = $chunk ? json_decode((string)$chunk->get('snippet'), true) : null;
if (!is_array($cfg) || empty($cfg['services']['default'])) return '';
$svc = 'default';
if (preg_match_all('~/uslugi/([a-z0-9-]+)~', (string)$res->get('content'), $m)) {
    foreach ($m[1] as $a) if (isset($cfg['aliases'][$a])) { $svc = $cfg['aliases'][$a]; break; }
}
$S = $cfg['services'][$svc] ?? $cfg['services']['default'];
$pos = (isset($pos) && $pos === 'mid') ? 'mid' : 'end';
$e = function ($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); };
$kicker = ''; $link = ''; $linkText = '';
if ($pos === 'mid') {
    $title = $tv('npCtaTitle'); $text = $tv('npCtaText'); $btn = $tv('npCtaButton');
    if ($title === '') {
        $d = $S['mid'] ?? $cfg['services']['default']['mid'];
        $title = $d['title']; $text = $d['text']; $btn = $btn !== '' ? $btn : $d['button'];
    }
    if ($btn === '') $btn = 'Обсудить мою задачу';
    $place = (int)$tv('npCtaPlace');
    if ($place < 2) $place = 3;
} else {
    $title = $S['title']; $text = $S['text']; $btn = $S['button'];
    $kicker = $S['kicker'] ?? ''; $link = $S['link'] ?? ''; $linkText = $S['linkText'] ?? '';
}
$uid = 'np-cta-' . $pos;
$form = $modx->runSnippet('AjaxForm', [
    'snippet' => 'FormIt',
    'hooks' => 'spam,email',
    'emailFrom' => 'info@' . $modx->getOption('http_host'),
    'form' => 'np_cta_form',
    'emailTpl' => 'np_cta_email',
    'emailSubject' => 'Непросто. Сообщение из формы обратной связи',
    'emailTo' => 'redegun@gmail.com,' . $modx->getOption('e-mail'),
    'validate' => 'name:required:stripTags,contact:required:stripTags,message:stripTags,cta:stripTags,email:blank',
    'successMessage' => 'Спасибо! Заявка отправлена, мы свяжемся с вами.',
    'validationErrorMessage' => '[[+errors]]',
    'errTpl' => '[[+error]]',
    'clearFieldsOnSuccess' => '1',
    'validationErrorBulkTpl' => '[[+error]]',
    'name.vTextRequired' => 'укажите имя',
    'contact.vTextRequired' => 'укажите телефон, почту или мессенджер',
    'frontend_js' => '[[+assetsUrl]]js/custom.js',
    'ctaId' => $uid,
    'ctaBlock' => $pos === 'mid' ? 'середина статьи' : 'конец статьи',
]);
$h = '<aside class="np-cta np-cta--' . $pos . '" aria-label="' . $e($title) . '">';
if ($kicker !== '') $h .= '<p class="np-cta__kicker">' . $e($kicker) . '</p>';
$h .= '<p class="np-cta__title">' . $e($title) . '</p>';
if ($text !== '' || $link !== '') {
    $h .= '<p class="np-cta__text">' . $e($text);
    if ($link !== '') $h .= ' <a class="np-cta__link" href="' . $e($link) . '">' . $e($linkText) . '</a>';
    $h .= '</p>';
}
$h .= '<details class="np-cta__details"><summary class="np-cta__button">' . $e($btn) . '</summary>'
    . '<div class="np-cta__panel">' . $form . '<div class="np-cta__result" role="status" aria-live="polite"></div></div></details></aside>';
if ($pos === 'mid') return '<div class="np-cta-slot" data-np-cta-place="' . $place . '">' . $h . '</div><i class="np-cta-slot-end"></i>';
return $h;
