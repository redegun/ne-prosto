<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir = __DIR__; $pub = "/home/r/redegun/ne-prosto/public_html/";
$r = $modx->getObject("modResource", 104) or die("no 104\n");
$mode = $argv[1] ?? "dry";
// backup
$bk = $r->toArray(); $bk["_tv_image"] = $r->getTVValue("image"); $bk["_tv_big"] = $r->getTVValue("page__image--big");
if (!file_exists("$dir/resource104.before.json")) file_put_contents("$dir/resource104.before.json", json_encode($bk, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
$c = $r->get("content");
if (strpos($c, "zayavki-messendzhery/") !== false) die("already has figures\n");
$fig = function($n, $alt) {
  $b = "/images/godnota/zayavki-messendzhery/$n";
  return "\n<figure class=\"np-article-figure\" style=\"margin:32px 0\"><img src=\"$b.jpg\" srcset=\"$b-768.jpg 768w, $b.jpg 1200w\" sizes=\"(max-width: 900px) 100vw, 900px\" width=\"1200\" height=\"800\" loading=\"lazy\" decoding=\"async\" alt=\"$alt\" style=\"display:block;width:100%;height:auto;border-radius:8px\"></figure>";
};
$ins = [
 ["<h2>Где теряются заявки</h2>", $fig("kanaly", "Телефоны, планшет и ноутбук с открытыми чатами, одно сообщение проваливается между ними")],
 ["<h2>Почему клиент не ждёт</h2>", $fig("klient-zhdet", "Клиент вечером ждёт ответа в мессенджере, а другая компания уже ответила")],
 ["<h2>Где помогает ИИ-ассистент</h2>", $fig("assistent", "Менеджер с кофе одним нажатием отправляет подготовленный черновик ответа клиенту")],
];
foreach ($ins as [$a, $html]) {
  $p = strpos($c, $a); if ($p === false) die("anchor not found: $a\n");
  $e = strpos($c, "</p>", $p); if ($e === false) die("no </p> after $a\n");
  $e += 4; $c = substr($c, 0, $e) . $html . substr($c, $e);
}
echo "new content len ", strlen($c), "\n";
if ($mode !== "apply") { file_put_contents("$dir/content.new.html", $c); exit("dry ok\n"); }
@mkdir($pub."images/godnota/zayavki-messendzhery", 0755);
foreach (glob("$dir/img/*.jpg") as $f) copy($f, $pub."images/godnota/zayavki-messendzhery/".basename($f));
$hero = "images/godnota/zayavki-messendzhery/hero.jpg";
$r->set("content", $c); $r->set("editedon", time()); $r->save();
$r->setTVValue("image", $hero);
$r->setTVValue("page__image--big", json_encode(["sourceImg"=>["src"=>$hero,"width"=>1536,"height"=>1024,"source"=>1],"crop"=>["x"=>0,"y"=>0,"width"=>1536,"height"=>1024],"targetWidth"=>0,"targetHeight"=>0]));
$modx->cacheManager->refresh();
$r2 = $modx->getObject("modResource", 104);
file_put_contents("$dir/resource104.after.json", json_encode($r2->toArray(), JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
echo "applied image=", $r2->getTVValue("image"), " big=", $r2->getTVValue("page__image--big"), "\n";
