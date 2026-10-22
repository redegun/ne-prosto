<?php
// task 503: create 8 hub articles (parent 2, template 8) — idempotent by alias
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir = __DIR__; $pub = "/home/r/redegun/ne-prosto/public_html/";
$mode = $argv[1] ?? "dry";
if (!file_exists("$dir/parent2-children.before.json")) {
  $kids=[]; foreach($modx->getCollection("modResource",["parent"=>2]) as $r) $kids[]=$r->toArray();
  file_put_contents("$dir/parent2-children.before.json", json_encode($kids, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
}
$modx->user = $modx->getObject("modUser", 1) ?: $modx->user;
$map = json_decode(file_get_contents("$dir/map.json"), true);
$mi = 13; $t0 = time(); $out = [];
foreach ($map as $n => [$alias, $img]) {
  $meta = json_decode(file_get_contents("$dir/a$n.meta.json"), true);
  $content = file_get_contents("$dir/a$n.html");
  $ex = $modx->getObject("modResource", ["alias"=>$alias, "parent"=>2]);
  if ($ex) { echo "exists $n id=",$ex->id,"\n"; $out[$n]=$ex->id; $mi++; continue; }
  if ($modx->getCount("modResource",["alias"=>$alias])) die("alias clash $alias\n");
  echo "will create $n $alias mi=$mi len=",strlen($content),"\n";
  if ($mode !== "apply") { $mi++; continue; }
  $res = $modx->runProcessor("resource/create", [
   "pagetitle"=>$meta["title"], "longtitle"=>"", "alias"=>$alias, "description"=>$meta["description"],
   "parent"=>2, "template"=>8, "published"=>1, "publishedon"=>date("Y-m-d H:i:s", $t0 + $mi), "hidemenu"=>0, "searchable"=>1, "cacheable"=>1,
   "richtext"=>1, "menuindex"=>$mi, "class_key"=>"modDocument", "context_key"=>"web", "content_type"=>1,
   "introtext"=>$meta["introtext"], "content"=>$content, "tvs"=>true,
   "tv1"=>$meta["seo_title"], "tv4"=>$meta["description"], "tv11"=>"0.7", "tv12"=>"weekly",
  ]);
  if ($res->isError()) { print_r($res->getAllErrors()); echo $res->getMessage(),"\n"; exit(1); }
  $o = $res->getObject(); $out[$n] = $o["id"]; echo "created $n id=",$o["id"],"\n"; $mi++;
}
file_put_contents("$dir/created.json", json_encode($out));
$modx->cacheManager->refresh();
