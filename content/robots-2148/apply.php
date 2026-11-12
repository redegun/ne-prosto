<?php
// task 2148: max-image-preview:large в meta robots (head, head_2019); noindex-страницы (TV noindex) без изменений
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$apply = getenv("NP_APPLY") === "1" || trim((string)@file_get_contents("/home/r/redegun/ne-prosto/_agent_archives/task2148/APPLY")) === "yes";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task2148"; @mkdir($bk, 0700, true);
function g($c, $m) { if (!$c) { echo "GUARD FAIL: $m\n"; exit(1); } }
$OLD = "[[*noindex]]";
$NEW = "[[*noindex:default=`<meta name=\"robots\" content=\"max-image-preview:large\">`]]";
$chunks = [];
foreach (["head" => "bb6563be702a8507279df18da76df24eaea1f18b7382eb2262d196609fbb83d5", "head_2019" => "c48a4a5f71b189654c35fd5c3eaae055b1a332fba7429473c6ea3fba8ebcd67e"] as $n => $h) {
  $o = $modx->getObject("modChunk", ["name" => $n]);
  g($o, "$n exists");
  $v = $o->get("snippet");
  g(hash("sha256", $v) === $h, "$n sha");
  g(substr_count($v, $OLD) === 1, "$n anchor");
  g(stripos($v, "max-image-preview") === false, "$n already has max-image-preview");
  $chunks[$n] = [$o, $v, str_replace($OLD, $NEW, $v)];
}
// пробный рендер тега на ресурсах: 60 (noindex), 61 (noindex, черновик), 1 (главная), 122 (статья), 14 (template 4)
$parser = $modx->getParser();
foreach ([60, 61, 1, 122, 14] as $id) {
  $r = $modx->getObject("modResource", $id);
  g($r, "res $id");
  $modx->resource = $r; $modx->resourceIdentifier = $id; $modx->elementCache = [];
  $s = $NEW;
  $parser->processElementTags("", $s, true, false, "[[", "]]", [], 10);
  $parser->processElementTags("", $s, true, true, "[[", "]]", [], 10);
  echo "render $id ", $r->get("uri"), " => ", $s, "\n";
  $want = in_array($id, [60, 61]) ? '<meta name="robots" content="noindex, nofollow">' : '<meta name="robots" content="max-image-preview:large">';
  g(trim($s) === $want, "render $id");
}
foreach ($chunks as $n => [$o, $v, $nv]) echo "$n new sha ", hash("sha256", $nv), "\n";
echo "guards ok\n";
if (!$apply) { echo "dry run\n"; exit(0); }
foreach ($chunks as $n => [$o, $v, $nv]) file_put_contents("$bk/$n.before.html", $v);
foreach ($chunks as $n => [$o, $v, $nv]) { $o->set("snippet", $nv); g($o->save(), "save $n"); }
$modx->cacheManager->refresh();
$out = [];
foreach ($chunks as $n => $_) { $v = $modx->getObject("modChunk", ["name" => $n])->get("snippet"); $out[$n] = hash("sha256", $v); file_put_contents("$bk/$n.after.html", $v); }
file_put_contents("$bk/after.json", json_encode($out, JSON_PRETTY_PRINT));
@unlink("$bk/APPLY");
echo json_encode($out, JSON_PRETTY_PRINT), "\n";
