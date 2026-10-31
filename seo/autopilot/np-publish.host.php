<?php
// task 862 (2026-10-31): публикатор статьи блога ne-prosto.ru для автопилота office-seo-ne-prosto-blog.
// Запуск: ssh -i ~/.ssh/ne-prosto_publish redegun@vh306 "/opt/php83/bin/php ~/ne-prosto/_autopilot/np-publish.php publish|dry|list" < payload.json
// Вход — JSON в stdin (собирает VPS sites/ne-prosto/seo/autopilot/publish.sh):
//  {alias, pagetitle, introtext, description, titl, content, cover_b64, cover768_b64, cover_w, cover_h,
//   images:[{name,b64}], cta:{title,text,button,place}}
// Создаёт ресурс parent 2 (/blog/), template 8, published=1 — как статьи хаба #503.
// Картинки: public_html/images/godnota/blog/<alias>.jpg (+ -768) и images/godnota/blog/<alias>/<name>.jpg.
// Коды: 0 ok, 3 дубль (alias уже есть), 2 ошибка входа, 1 сбой.
$mode = $argv[1] ?? "dry";
$D = __DIR__; $pub = "/home/r/redegun/ne-prosto/public_html/";
function out($a, $code = 0) { echo json_encode($a, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES), "\n"; exit($code); }
define("MODX_API_MODE", true);
require $pub . "index.php";
$modx->user = $modx->getObject("modUser", 1) ?: $modx->user;
if ($mode === "list") {
  $c = $modx->newQuery("modResource", ["parent"=>2]); $c->sortby("id","ASC"); $r = [];
  foreach ($modx->getCollection("modResource",$c) as $x) $r[] = ["id"=>$x->id,"alias"=>$x->alias,"published"=>(int)$x->published,"pagetitle"=>$x->pagetitle];
  out(["success"=>true,"items"=>$r]);
}
$in = json_decode(stream_get_contents(STDIN), true);
if (!is_array($in)) out(["success"=>false,"error"=>"bad json"], 2);
$alias = (string)($in["alias"] ?? "");
if (!preg_match('/^[a-z0-9-]{3,90}$/', $alias)) out(["success"=>false,"error"=>"bad alias"], 2);
foreach (["pagetitle","introtext","description","titl","content","cover_b64","cover768_b64"] as $k)
  if (trim((string)($in[$k] ?? "")) === "") out(["success"=>false,"error"=>"missing $k"], 2);
if (mb_strlen($in["pagetitle"]) > 120 || mb_strlen($in["titl"]) > 90) out(["success"=>false,"error"=>"title too long"], 2);
if (stripos($in["content"], "<h1") !== false) out(["success"=>false,"error"=>"content has h1"], 2);
if (preg_match('/<\?php|<\?=|\[\[!?(?:\$|\+\+|\*|-)?[A-Za-z]/', $in["content"])) out(["success"=>false,"error"=>"content has php/modx tags"], 2);
$cover = base64_decode($in["cover_b64"], true); $c768 = base64_decode($in["cover768_b64"], true);
if (!$cover || !$c768 || substr($cover,0,2) !== "\xFF\xD8" || substr($c768,0,2) !== "\xFF\xD8") out(["success"=>false,"error"=>"cover must be jpeg"], 2);
$imgs = [];
foreach (($in["images"] ?? []) as $im) {
  $n = (string)($im["name"] ?? ""); $b = base64_decode((string)($im["b64"] ?? ""), true);
  if (!preg_match('/^[a-z0-9-]{2,60}$/', $n) || !$b || substr($b,0,2) !== "\xFF\xD8") out(["success"=>false,"error"=>"bad image $n"], 2);
  $imgs[$n] = $b;
}
if (count($imgs) > 4) out(["success"=>false,"error"=>"too many images"], 2);
$ex = $modx->getObject("modResource", ["alias"=>$alias]);
if ($ex) out(["success"=>false,"error"=>"exists","id"=>$ex->id,"published"=>(int)$ex->published,"url"=>"https://ne-prosto.ru/".$ex->uri], 3);
if ($mode !== "publish") out(["success"=>true,"dry"=>true,"alias"=>$alias,"content_chars"=>mb_strlen(strip_tags($in["content"])),"images"=>array_keys($imgs)]);

$rel = "images/godnota/blog/";
@mkdir($pub.$rel, 0755, true);
if (file_put_contents($pub.$rel."$alias.jpg", $cover) === false || file_put_contents($pub.$rel."$alias-768.jpg", $c768) === false) out(["success"=>false,"error"=>"write cover"], 1);
if ($imgs) { @mkdir($pub.$rel.$alias, 0755, true); foreach ($imgs as $n => $b) if (file_put_contents($pub.$rel."$alias/$n.jpg", $b) === false) out(["success"=>false,"error"=>"write image $n"], 1); }
[$w, $h] = getimagesize($pub.$rel."$alias.jpg");
$c = $modx->newQuery("modResource", ["parent"=>2]); $c->sortby("menuindex","DESC"); $c->limit(1);
$last = $modx->getObject("modResource", $c); $mi = $last ? $last->menuindex + 1 : 0;
$res = $modx->runProcessor("resource/create", [
  "pagetitle"=>$in["pagetitle"], "longtitle"=>"", "alias"=>$alias, "description"=>$in["description"],
  "parent"=>2, "template"=>8, "published"=>1, "publishedon"=>date("Y-m-d H:i:s"), "hidemenu"=>0, "searchable"=>1, "cacheable"=>1,
  "richtext"=>1, "menuindex"=>$mi, "class_key"=>"modDocument", "context_key"=>"web", "content_type"=>1,
  "introtext"=>$in["introtext"], "content"=>$in["content"], "tvs"=>true,
  "tv1"=>$in["titl"], "tv4"=>$in["description"], "tv11"=>"0.7", "tv12"=>"weekly",
]);
if ($res->isError()) out(["success"=>false,"error"=>"create: ".$res->getMessage(),"errors"=>$res->getAllErrors()], 1);
$o = $res->getObject(); $r = $modx->getObject("modResource", $o["id"]);
$p = $rel."$alias.jpg";
$r->setTVValue("image", $p);
$r->setTVValue("page__image--big", json_encode(["sourceImg"=>["src"=>$p,"width"=>$w,"height"=>$h,"source"=>1],"crop"=>["x"=>0,"y"=>0,"width"=>$w,"height"=>$h],"targetWidth"=>0,"targetHeight"=>0]));
$cta = $in["cta"] ?? [];
if (!empty($cta["title"])) $r->setTVValue("npCtaTitle", $cta["title"]);
if (!empty($cta["text"])) $r->setTVValue("npCtaText", $cta["text"]);
if (!empty($cta["button"])) $r->setTVValue("npCtaButton", $cta["button"]);
if (!empty($cta["place"])) $r->setTVValue("npCtaPlace", (string)(int)$cta["place"]);
$modx->cacheManager->refresh();
@mkdir("$D/log", 0700);
file_put_contents("$D/log/".date("Ymd-His")."-$alias.json", json_encode(["id"=>$r->id,"alias"=>$alias,"pagetitle"=>$in["pagetitle"],"menuindex"=>$mi,"images"=>array_keys($imgs)], JSON_UNESCAPED_UNICODE));
out(["success"=>true,"id"=>$r->id,"alias"=>$alias,"url"=>"https://ne-prosto.ru/blog/$alias"]);
