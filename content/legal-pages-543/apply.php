<?php
// task 543: политика + согласие, ссылки в подвале, звёздочки и галочка согласия во всех формах
define('MODX_API_MODE', true);
require '/home/r/redegun/ne-prosto/public_html/index.php';
$dir = __DIR__; $mode = $argv[1] ?? 'dry';
$A = '/home/r/redegun/ne-prosto/public_html/assets/neprosto/design-20261018/';
$POL = '/politika-konfidencialnosti'; $SOG = '/soglasie-na-obrabotku-personalnyh-dannyh';
@mkdir("$dir/before"); @mkdir("$dir/after");
function bk($name, $c) { global $dir; if (!file_exists("$dir/before/$name")) file_put_contents("$dir/before/$name", $c); }
function rep($c, $a, $b, $what) { if (substr_count($c, $a) !== 1) die("anchor not unique in $what: $a\n"); return str_replace($a, $b, $c); }
if ($modx->getCount('modResource', ['uri:IN' => [ltrim($POL,'/'), ltrim($SOG,'/')]])) die("pages already exist\n");

$consent = function ($cls, $extra = '') use ($POL, $SOG) {
  return '<div class="np-consent ' . $cls . '"><label class="np-consent__label"><input type="checkbox" name="policy" value="1" required>'
   . '<span>Я согласен на <a href="' . $SOG . '" target="_blank">обработку персональных данных</a> и принимаю <a href="' . $POL . '" target="_blank">политику конфиденциальности</a></span></label>'
   . $extra . '<p class="np-req-note">* обязательные поля</p></div>';
};
$star = ' <span class="np-req" aria-hidden="true">*</span>';
$ch = []; // id => new content

// 1. «Обсудить проект» (request_form 93)
$c = $modx->getObject('modChunk', 93)->get('snippet'); bk('chunk93.html', $c);
$c = rep($c, '<label for="np-name">Ваше имя</label>', '<label for="np-name">Ваше имя' . $star . '</label>', 'c93');
$c = rep($c, '<label for="np-contact">Электронная почта</label>', '<label for="np-contact">Электронная почта' . $star . '</label>', 'c93');
$c = rep($c, "\t\t\t\t<label class=\"form-field form-field_attachment\">", "\t\t\t\t" . $consent('form-field form-field_consent') . "\n\t\t\t\t<label class=\"form-field form-field_attachment\">", 'c93');
$c = rep($c, '&validate=`contact:email:required,name:required,email:blank`', '&validate=`contact:email:required,name:required,email:blank,policy:required`', 'c93');
$c = rep($c, '&contact.vTextRequired=', "&policy.vTextRequired=`отметьте&nbsp;согласие на&nbsp;обработку персональных данных`\n&contact.vTextRequired=", 'c93');
$ch[93] = $c;

// 2. CTA в статьях (np_cta_form 106 + сниппет 98)
$c = $modx->getObject('modChunk', 106)->get('snippet'); bk('chunk106.html', $c);
$c = rep($c, '-name">Имя</label>', '-name">Имя' . $star . '</label>', 'c106');
$c = rep($c, '-contact">Телефон, почта или мессенджер</label>', '-contact">Телефон, почта или мессенджер' . $star . '</label>', 'c106');
$c = rep($c, '<button type="submit"', $consent('np-cta-form__field np-cta-form__field--wide', '<span class="error_policy np-cta-form__error"></span>') . "\n<button type=\"submit\"", 'c106');
$ch[106] = $c;
$s = $modx->getObject('modSnippet', 98); $sc = $s->get('snippet'); bk('snippet98.php', $sc);
$sc = rep($sc, "cta:stripTags,email:blank',", "cta:stripTags,email:blank,policy:required',", 's98');
$sc = rep($sc, "    'contact.vTextRequired' =>", "    'policy.vTextRequired' => 'отметьте согласие на обработку персональных данных',\n    'contact.vTextRequired' =>", 's98');

// 3. Отклик на вакансию (form--job 42 + jobs__item 40)
$c = $modx->getObject('modChunk', 42)->get('snippet'); bk('chunk42.html', $c);
$c = rep($c, 'placeholder="Представьтесь"', 'placeholder="Представьтесь *"', 'c42');
$c = rep($c, 'placeholder="Почта"', 'placeholder="Почта *"', 'c42');
$c = rep($c, 'placeholder="Расскажите о себе"', 'placeholder="Расскажите о себе *"', 'c42');
$c = rep($c, "    \t<div class=\"form__button-wrap\">", "    \t" . $consent('jobs__consent') . "\n    \t<div class=\"form__button-wrap\">", 'c42');
$ch[42] = $c;
$c = $modx->getObject('modChunk', 40)->get('snippet'); bk('chunk40.html', $c);
$c = rep($c, 'message:minLength=^12^`', 'message:minLength=^12^,policy:required`', 'c40');
$c = rep($c, "            \t&name.vTextRequired=", "            \t&policy.vTextRequired=`отметьте&nbsp;согласие на&nbsp;обработку персональных данных`\n            \t&name.vTextRequired=", 'c40');
$ch[40] = $c;

// 4. Подвал (np_footer 98)
$c = $modx->getObject('modChunk', 98)->get('snippet'); bk('chunk98.html', $c);
$c = rep($c, 'Не забывайте указывать источник — ne-prosto.ru.</p>', 'Не забывайте указывать источник — ne-prosto.ru.</p><p class="np-footer__legal"><a href="' . $POL . '">Политика конфиденциальности</a><a href="' . $SOG . '">Согласие на обработку персональных данных</a></p>', 'c98');
$ch[98] = $c;

// 5. Версии CSS: site.css в head (11, 89), article.css в template 8
foreach ([11, 89] as $id) { $c = $modx->getObject('modChunk', $id)->get('snippet'); bk("chunk$id.html", $c); $ch[$id] = rep($c, 'site.css?v=9', 'site.css?v=10', "c$id"); }
$t8 = $modx->getObject('modTemplate', 8); $t8c = $t8->get('content'); bk('template8.html', $t8c);
$t8n = rep($t8c, 'article.css?v=8', 'article.css?v=9', 't8');

$css = file_get_contents($A . 'site.css'); bk('site.css', $css);
$acss = file_get_contents($A . 'article.css'); bk('article.css', $acss);
if (strpos($css, 'task 543') !== false) die("css already\n");
$css .= "\n/* task 543: звёздочки обязательных полей, галочка согласия, ссылки на документы в подвале */\n"
 . ".np-site .np-consent{grid-column:1/-1;margin:0;font-size:15px;line-height:1.45;color:var(--np-ink)}"
 . ".np-site .np-consent .np-consent__label{display:flex!important;align-items:flex-start;gap:10px;margin:0!important;font-size:15px!important;line-height:1.45;color:inherit!important;cursor:pointer}"
 . ".np-site .np-consent input[type=checkbox]{-webkit-appearance:checkbox;appearance:auto;display:inline-block!important;flex:0 0 auto;width:18px!important;height:18px!important;min-height:0!important;margin:2px 0 0!important;padding:0!important;border:0!important;position:static!important;opacity:1!important;accent-color:#191b18;cursor:pointer}"
 . ".np-site .np-consent a{color:inherit;text-decoration:underline}"
 . ".np-site .np-req-note{margin:8px 0 0!important;font-size:13px;color:var(--np-muted)}"
 . ".np-site .jobs__consent{margin:20px 0}"
 . ".np-footer__legal{display:flex;flex-direction:column;align-items:start;gap:6px;margin-top:16px!important;font-size:13px}.np-footer__legal a{color:#b7bcb0}\n";
$acss .= "\n/* task 543: галочка согласия в форме CTA */\n.np-cta-form .np-consent{grid-column:1/-1}.np-cta-form .np-consent label{font-size:14px!important}\n";

foreach ($ch as $id => $c) file_put_contents("$dir/after/chunk$id.html", $c);
file_put_contents("$dir/after/snippet98.php", $sc); file_put_contents("$dir/after/template8.html", $t8n);
file_put_contents("$dir/after/site.css", $css); file_put_contents("$dir/after/article.css", $acss);
if ($mode !== 'apply') { echo "dry ok: chunks " . implode(',', array_keys($ch)) . ", snippet 98, template 8, css\n"; exit; }

// шаблон «Документ»
$tpl = $modx->getObject('modTemplate', ['templatename' => 'Документ']);
if (!$tpl) {
  $tpl = $modx->newObject('modTemplate');
  $tpl->fromArray(['templatename' => 'Документ', 'description' => 'task 543: политика, согласие и другие юр. тексты', 'content' => file_get_contents("$dir/template-doc.html")]);
  $tpl->save();
}
$now = time();
foreach ([[ltrim($POL,'/'), 'Политика конфиденциальности', 'Политика ИП Ветров А.А. в отношении обработки персональных данных', 'Политика в отношении обработки персональных данных пользователей сайта ne-prosto.ru: какие данные собираем, зачем, как храним и как отозвать согласие.', 'policy.html'],
          [ltrim($SOG,'/'), 'Согласие на обработку персональных данных', 'Согласие на обработку персональных данных', 'Согласие на обработку персональных данных, которое пользователь даёт, отправляя форму на сайте ne-prosto.ru.', 'consent.html']] as [$alias, $pt, $lt, $desc, $f]) {
  $r = $modx->newObject('modResource');
  $r->fromArray(['pagetitle' => $pt, 'longtitle' => $lt, 'menutitle' => $pt, 'description' => $desc, 'alias' => $alias, 'uri' => $alias, 'parent' => 0, 'template' => $tpl->get('id'),
    'published' => 1, 'publishedon' => $now, 'createdon' => $now, 'hidemenu' => 1, 'searchable' => 1, 'richtext' => 0, 'cacheable' => 1, 'class_key' => 'modDocument', 'content_type' => 1,
    'context_key' => 'web', 'content' => file_get_contents("$dir/$f")]);
  if (!$r->save()) die("save $alias failed\n");
  echo "resource {$r->id} {$r->uri}\n";
}
foreach ($ch as $id => $c) { $o = $modx->getObject('modChunk', $id); $o->set('snippet', $c); $o->save(); }
$s->set('snippet', $sc); $s->save();
$t8->set('content', $t8n); $t8->save();
file_put_contents($A . 'site.css', $css); file_put_contents($A . 'article.css', $acss);
$modx->cacheManager->refresh();
echo "applied, template {$tpl->id}\n";
