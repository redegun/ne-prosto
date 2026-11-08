<?php
// task 1726: живые обложки Stageshow — np_project, np_ss_case, head/head_2019, контент 83/84/85
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$apply = in_array(getenv("NP_APPLY"), ["1"], true) || trim((string)@file_get_contents("/home/r/redegun/ne-prosto/_agent_archives/task1726/APPLY")) === "yes";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task1726"; @mkdir($bk, 0700, true);
$asd = "/home/r/redegun/ne-prosto/public_html/assets/neprosto/stageshow";
function g($c, $m) { if (!$c) { echo "GUARD FAIL: $m\n"; exit(1); } }
$np = $modx->getObject("modChunk", ["name" => "np_project"]); $npv = $np->get("snippet");
g(hash("sha256", $npv) === "a43cd19b000c4a683e473ca06acef74c724b69bb5bd8d5e80913f8012dca47ff", "np_project sha");
$heads = [];
foreach (["head" => "697e60d44b1163b1d9d783f1649777b67de69ed8133dec74e2f20b739730c03f", "head_2019" => "12b858c09b3c47c3bd3b7a2c41a60a47b871a0c4080f19e3d4df73cb651ceb64"] as $n => $h) {
  $o = $modx->getObject("modChunk", ["name" => $n]);
  g(hash("sha256", $o->get("snippet")) === $h, "$n sha");
  g(substr_count($o->get("snippet"), 'site.js?v=9"></script>') === 1, "$n anchor");
  $heads[$n] = $o;
}
$res = [];
foreach (["83" => "9f40f8a44918b54de90bac77f9a15b25b2ca708aaea6175e41a3ea1435779605", "84" => "af31febd00c903f656ee9beb383b591292a62f1f3a2d89154d29f6815ea68801", "85" => "ff8982ad6b282b71c7ed29b3d4eb23539e55c9735b877bfa23c9b6ebd1389bcf"] as $id => $h) {
  $r = $modx->getObject("modResource", (int)$id);
  g(hash("sha256", $r->get("content")) === $h, "res $id sha");
  $res[$id] = $r;
}
g(!$modx->getObject("modChunk", ["name" => "np_ss_case"]), "np_ss_case exists");
g(!file_exists("$asd/stageshow.css") && !file_exists("$asd/stageshow.js"), "assets exist");
// пробный рендер карточки через pdoTools до записи
$pdo = $modx->getService("pdoTools");
$newnp = base64_decode("@@NP@@");
foreach (["portfolio/vinyl-tm", "portfolio/firmaflis"] as $u) {
  $html = $pdo->getChunk("@INLINE " . $newnp, ["uri" => $u, "pagetitle" => "T", "longtitle" => "", "introtext" => "x", "tv.image" => "assets/x.jpg"]);
  echo "render $u: video=", substr_count($html, "<video"), " img=", substr_count($html, "<img"), " braces=", substr_count($html, "{\$"), "\n";
}
echo "guards ok\n";
if (!$apply) { echo "dry run\n"; exit(0); }
file_put_contents("$bk/np_project.before.html", $npv);
foreach ($heads as $n => $o) file_put_contents("$bk/$n.before.html", $o->get("snippet"));
foreach ($res as $id => $r) file_put_contents("$bk/res$id.content.before.html", $r->get("content"));
file_put_contents("$asd/stageshow.css", base64_decode("@@CSS@@"));
file_put_contents("$asd/stageshow.js", base64_decode("@@JS@@"));
$c = $modx->newObject("modChunk"); $c->set("name", "np_ss_case"); $c->set("description", "task 1726: живая обложка Stageshow на странице кейса");
$c->set("snippet", base64_decode("@@CASE@@")); g($c->save(), "save np_ss_case");
$np->set("snippet", $newnp); g($np->save(), "save np_project");
$link = base64_decode("@@LINK@@");
foreach ($heads as $n => $o) { $o->set("snippet", str_replace('site.js?v=9"></script>', 'site.js?v=9"></script>' . $link, $o->get("snippet"))); g($o->save(), "save $n"); }
$calls = json_decode(base64_decode("@@CALLS@@"), true);
foreach ($res as $id => $r) { $r->set("content", $calls[$id] . "\n" . $r->get("content")); g($r->save(), "save res $id"); }
$modx->cacheManager->refresh();
$out = ["np_project" => hash("sha256", $modx->getObject("modChunk", ["name" => "np_project"])->get("snippet")),
        "np_ss_case" => hash("sha256", $modx->getObject("modChunk", ["name" => "np_ss_case"])->get("snippet"))];
foreach ($heads as $n => $o) { $v = $modx->getObject("modChunk", ["name" => $n])->get("snippet"); $out[$n] = hash("sha256", $v); file_put_contents("$bk/$n.after.html", $v); }
foreach ($res as $id => $r) $out["res$id"] = hash("sha256", $modx->getObject("modResource", (int)$id)->get("content"));
file_put_contents("$bk/after.json", json_encode($out, JSON_PRETTY_PRINT));
echo json_encode($out, JSON_PRETTY_PRINT), "\n";
