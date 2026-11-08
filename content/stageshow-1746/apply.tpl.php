<?php
// task 1746: vinyl-tm — 3 доп. ролика у разделов кейса (res 83), чередование в карточке (np_project), stageshow.js?v=2 в head/head_2019
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task1746"; @mkdir($bk, 0700, true);
$apply = trim((string)@file_get_contents("$bk/APPLY")) === "yes";
$D = json_decode(base64_decode("@@DATA@@"), true);
function g($c, $m) { if (!$c) { echo "GUARD FAIL: $m\n"; exit(1); } }
$np = $modx->getObject("modChunk", ["name" => "np_project"]); $npv = $np->get("snippet");
g(substr_count($npv, $D["np_old"]) === 1, "np_old");
g(substr_count($npv, $D["v_old"]) === 1, "v_old");
g(strpos($npv, "data-ss-alt") === false, "already alt");
$newnp = str_replace([$D["np_old"], $D["v_old"]], [$D["np_new"], $D["v_new"]], $npv);
$heads = [];
foreach (["head", "head_2019"] as $h) { $o = $modx->getObject("modChunk", ["name" => $h]); g(substr_count($o->get("snippet"), $D["js_old"]) === 1, "$h js"); $heads[$h] = $o; }
$r = $modx->getObject("modResource", 83); $rc = $r->get("content");
g($r->get("uri") === "portfolio/vinyl-tm", "res83 uri");
g(substr_count($rc, $D["anchor"]) === 1, "res83 anchor");
g(strpos($rc, "np-vinyl-marki") === false, "res83 already");
foreach (["np-vinyl-marki", "np-vinyl-goroda", "np-vinyl-raboty"] as $n) foreach (["$n-1440.webm", "$n-1440.mp4", "$n-390.webm", "$n-390.mp4", "poster-1440.png", "poster-390.png"] as $f)
  g(is_file("/home/r/redegun/ne-prosto/public_html/assets/neprosto/stageshow/$n/$f"), "asset $n/$f");
$pdo = $modx->getService("pdoTools");
foreach (["portfolio/vinyl-tm", "portfolio/kppf", "portfolio/iris"] as $u) {
  $html = $pdo->getChunk("@INLINE " . $newnp, ["uri" => $u, "pagetitle" => "T", "longtitle" => "", "introtext" => "x", "tv.image" => "assets/x.jpg"]);
  echo "render $u: video=", substr_count($html, "<video"), " alt=", substr_count($html, "data-ss-alt=\"np-vinyl-marki"), " img=", substr_count($html, "<img"), " braces=", substr_count($html, "{\$"), "\n";
}
echo "sha np_project=", hash("sha256", $npv), " res83=", hash("sha256", $rc), "\n";
echo "guards ok\n";
if (!$apply) { echo "dry run\n"; exit(0); }
file_put_contents("$bk/np_project.before.html", $npv);
file_put_contents("$bk/res83.content.before.html", $rc);
foreach ($heads as $h => $o) file_put_contents("$bk/$h.before.html", $o->get("snippet"));
$np->set("snippet", $newnp); g($np->save(), "save np_project");
foreach ($heads as $h => $o) { $o->set("snippet", str_replace($D["js_old"], $D["js_new"], $o->get("snippet"))); g($o->save(), "save $h"); }
$r->set("content", str_replace($D["anchor"], $D["block"] . $D["anchor"], $rc)); g($r->save(), "save res83");
$modx->cacheManager->refresh();
$out = ["np_project" => hash("sha256", $modx->getObject("modChunk", ["name" => "np_project"])->get("snippet")),
  "res83" => hash("sha256", $modx->getObject("modResource", 83)->get("content"))];
foreach (["head", "head_2019"] as $h) $out[$h] = hash("sha256", $modx->getObject("modChunk", ["name" => $h])->get("snippet"));
file_put_contents("$bk/after.json", json_encode($out, JSON_PRETTY_PRINT));
echo json_encode($out, JSON_PRETTY_PRINT), "\n";
