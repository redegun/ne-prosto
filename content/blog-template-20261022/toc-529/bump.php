<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir=__DIR__; $t=$modx->getObject("modTemplate",8); $c=$t->get("content");
foreach(["article.css?v=3","article.js?v=2"] as $g) if (substr_count($c,$g)!==1) die("guard: $g count=".substr_count($c,$g)."\n");
file_put_contents("$dir/template8.before.html",$c);
$d="/home/r/redegun/ne-prosto/public_html/assets/neprosto/design-20261018";
copy("$dir/article.after.css","$d/article.css"); copy("$dir/article.after.js","$d/article.js");
$n=str_replace(["article.css?v=3","article.js?v=2"],["article.css?v=4","article.js?v=3"],$c);
$t->set("content",$n); $t->save(); $modx->cacheManager->refresh();
file_put_contents("$dir/template8.after.html",$n);
echo "ok before=",hash("sha256",$c)," after=",hash("sha256",$modx->getObject("modTemplate",8)->get("content")),"\n";
