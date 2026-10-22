<?php
// task 538: CTA в статьях блога — TV, чанки, сниппет, плагин, template 8, article.css/js
define('MODX_API_MODE', true);
require '/home/r/redegun/ne-prosto/public_html/index.php';
$dir = __DIR__; $mode = $argv[1] ?? 'dry';
$A = '/home/r/redegun/ne-prosto/public_html/assets/neprosto/design-20261018/';
$t = $modx->getObject('modTemplate', 8); $tc = $t->get('content');
if (sha1($tc) !== '1364db3d402e522946c9618758f71cdaa6febcc6') die("template 8 changed\n");
if (strpos($tc, 'npArticleCta') !== false) die("already applied\n");
$new = $tc;
$rep = [
 "[[*content]]\n" => "[[*content]]\n[[!npArticleCta? &pos=`mid`]]\n",
 "[[*author:notempty=`<div class=\"post__autor\">[[*author]]</div>`]]\n" => "[[*author:notempty=`<div class=\"post__autor\">[[*author]]</div>`]]\n[[!npArticleCta? &pos=`end`]]\n",
 'article.css?v=4' => 'article.css?v=5',
 'article.js?v=3' => 'article.js?v=4',
];
foreach ($rep as $a => $b) { if (substr_count($new, $a) !== 1) die("anchor not unique: $a\n"); $new = str_replace($a, $b, $new); }
file_put_contents("$dir/template8.after.html", $new);
$css = file_get_contents($A.'article.css'); $js = file_get_contents($A.'article.js');
if (strpos($css, 'task 538') !== false) die("css already\n");
$texts = json_decode(file_get_contents("$dir/texts.json"), true);
if (count($texts) !== 9) die("texts\n");
echo "template ok, sha after ".sha1($new)."\n";
if ($mode !== 'apply') { echo "dry ok\n"; exit; }
copy($A.'article.css', "$dir/article.before.css"); copy($A.'article.js', "$dir/article.before.js");
$el = function ($class, $key, $name, $field, $code, $desc) use ($modx) {
  $o = $modx->getObject($class, [$key => $name]) ?: $modx->newObject($class);
  $o->fromArray([$key => $name, 'description' => $desc]); $o->set($field, $code);
  if (!$o->save()) die("save $name failed\n"); echo "$class $name id=".$o->get('id')."\n"; return $o;
};
$el('modChunk', 'name', 'np_cta_form', 'snippet', file_get_contents("$dir/np_cta_form.html"), 'task 538: форма в призыве статьи блога');
$el('modChunk', 'name', 'np_cta_email', 'snippet', file_get_contents("$dir/np_cta_email.html"), 'task 538: письмо из призыва статьи');
$el('modChunk', 'name', 'np_cta_services', 'snippet', file_get_contents("$dir/np_cta_services.json"), 'task 538: тексты призывов по услугам (JSON; aliases — адрес услуги → ключ)');
$el('modSnippet', 'name', 'npArticleCta', 'snippet', preg_replace('~^<\?php\s*~', '', file_get_contents("$dir/snippet.php")), 'task 538: призывы в статьях блога');
$pl = $el('modPlugin', 'name', 'npArticleCtaPlace', 'plugincode', preg_replace('~^<\?php\s*~', '', file_get_contents("$dir/plugin.php")), 'task 538: ставит средний призыв статьи перед N-м H2');
$pl->set('disabled', 0); $pl->save();
$ev = $modx->getObject('modPluginEvent', ['pluginid' => $pl->get('id'), 'event' => 'OnWebPagePrerender']);
if (!$ev) { $ev = $modx->newObject('modPluginEvent'); $ev->set('pluginid', $pl->get('id')); $ev->set('event', 'OnWebPagePrerender'); }
$ev->set('priority', -200); $ev->save();
$tvs = [
 'npCtaMode' => ['listbox', 'Призывы в статье', 'Авто — показывать в новых статьях (id от 104). Выключить / Включить — вручную, в т.ч. для старых статей', 'Авто==||Выключить==off||Включить==on'],
 'npCtaTitle' => ['text', 'Призыв в середине: заголовок', 'Пусто — текст по услуге из чанка np_cta_services', ''],
 'npCtaText' => ['textarea', 'Призыв в середине: текст', '1–2 строки под заголовком', ''],
 'npCtaButton' => ['text', 'Призыв в середине: кнопка', 'Кнопка раскрывает форму', ''],
 'npCtaPlace' => ['text', 'Призыв в середине: перед каким H2', 'Номер подзаголовка H2, перед которым стоит блок (по умолчанию 3)', ''],
];
$rank = 50;
foreach ($tvs as $name => [$type, $caption, $desc, $elements]) {
  $tv = $modx->getObject('modTemplateVar', ['name' => $name]) ?: $modx->newObject('modTemplateVar');
  $tv->fromArray(['name' => $name, 'type' => $type, 'caption' => $caption, 'description' => $desc, 'elements' => $elements, 'rank' => $rank++, 'default_text' => '']);
  if (!$tv->save()) die("tv $name\n");
  if (!$modx->getObject('modTemplateVarTemplate', ['tmplvarid' => $tv->get('id'), 'templateid' => 8])) {
    $l = $modx->newObject('modTemplateVarTemplate'); $l->set('tmplvarid', $tv->get('id')); $l->set('templateid', 8); $l->set('rank', $rank); $l->save();
  }
  echo "tv $name id=".$tv->get('id')."\n";
}
foreach ($texts as $id => [$ti, $tx, $bt, $place]) {
  $r = $modx->getObject('modResource', (int)$id);
  $r->setTVValue('npCtaTitle', $ti); $r->setTVValue('npCtaText', $tx); $r->setTVValue('npCtaButton', $bt);
  if ((int)$place !== 3) $r->setTVValue('npCtaPlace', (string)$place);
  echo "tv values $id\n";
}
file_put_contents($A.'article.css', $css.file_get_contents("$dir/cta.css"));
file_put_contents($A.'article.js', $js.file_get_contents("$dir/cta.js"));
$t->set('content', $new); if (!$t->save()) die("template save\n");
$modx->cacheManager->refresh();
echo "applied\n";
