<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$r = $modx->getObject("modResource", 103); $c = $r->get("content");
file_put_contents(__DIR__."/r103.before-fix.html", $c);
if (!preg_match('~<section><h2>Полезно почитать</h2><ul>(.*?)</ul></section>~su', $c, $m)) die("block not found\n");
$new = "<section><h2>Полезно почитать</h2>".preg_replace('~<li>(.*?)</li>~su', '<p>$1</p>', $m[1])."</section>";
$c = str_replace($m[0], $new, $c); $r->set("content", $c); $r->save();
$modx->cacheManager->refresh(); echo "fixed ", substr_count($new, "<p>"), "\n";
