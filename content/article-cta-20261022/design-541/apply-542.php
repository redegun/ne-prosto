<?php
// task 542: CTA вариант 1 (#541) — дописать в article.css, v=7 -> v=8 в template 8
define('MODX_API_MODE', true);
require '/home/r/redegun/ne-prosto/public_html/index.php';
$dir = __DIR__; $A = '/home/r/redegun/ne-prosto/public_html/assets/neprosto/design-20261018/';
$t = $modx->getObject('modTemplate', 8); $tc = $t->get('content');
file_put_contents("$dir/template8.before.html", $tc);
if (substr_count($tc, 'article.css?v=7') !== 1) die("template: v=7 not found once\n");
if (sha1_file($A.'article.css') !== 'bb36f1c970fdc468f31ddf876716cb397e68c8a0') die("article.css changed\n");
$new = str_replace('article.css?v=7', 'article.css?v=8', $tc);
file_put_contents($A.'article.css', file_get_contents("$dir/article.before.css").file_get_contents("$dir/cta542.css"));
$t->set('content', $new); $t->save(); file_put_contents("$dir/template8.after.html", $new);
$modx->cacheManager->refresh(); echo "ok before=".sha1($tc)." after=".sha1($new)."\n";
