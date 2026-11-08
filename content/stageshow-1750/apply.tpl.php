<?php
// task 1750: vinyl-tm — шапка ×1000, главный ролик np-vinyl-calc (без абсолютных визитов), раздел «Органика по Метрике», organika в чередование карточки
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task1750"; @mkdir($bk, 0700, true);
$ss = "/home/r/redegun/ne-prosto/public_html/assets/neprosto/stageshow";
$apply = trim((string)@file_get_contents("$bk/APPLY")) === "yes";
$D = json_decode(base64_decode("@@DATA@@"), true);
function g($c, $m) { if (!$c) { echo "GUARD FAIL: $m\n"; exit(1); } }
$np = $modx->getObject("modChunk", ["name" => "np_project"]); $npv = $np->get("snippet");
$newnp = $npv;
foreach ($D["np"] as $p) { g(substr_count($npv, $p[0]) === 1, "np_project: " . substr($p[0], 0, 40)); $newnp = str_replace($p[0], $p[1], $newnp); }
$r = $modx->getObject("modResource", 83); $rc = $r->get("content");
g($r->get("uri") === "portfolio/vinyl-tm", "res83 uri");
g(strpos($rc, "np-vinyl-organika") === false, "res83 already");
$new = $rc;
foreach ($D["r"] as $p) { g(substr_count($rc, $p[0]) === 1, "res83: " . substr($p[0], 0, 60)); $new = str_replace($p[0], $p[1], $new); }
g(substr_count($new, $D["anchor"]) === 1, "res83 anchor");
$new = str_replace($D["anchor"], $D["section"] . $D["anchor"], $new);
foreach (["20 000", "20&nbsp;000", "~20", "около 20"] as $bad) g(strpos($new, $bad) === false, "left: $bad");
$src = "$bk/files";
$sets = ["np-vinyl", "np-vinyl-calc", "np-vinyl-organika"];
foreach ($sets as $n) foreach (["$n-1440.webm", "$n-1440.mp4", "$n-390.webm", "$n-390.mp4", "poster-1440.png", "poster-390.png"] as $f) g(filesize("$src/$n/$f") > 1000, "staged $n/$f");
g(!is_dir("$ss/np-vinyl-calc") && !is_dir("$ss/np-vinyl-organika"), "asset dirs exist");
g(is_dir("$ss/np-vinyl"), "np-vinyl dir");
$pdo = $modx->getService("pdoTools");
$html = $pdo->getChunk("@INLINE " . $newnp, ["uri" => "portfolio/vinyl-tm", "pagetitle" => "T", "longtitle" => "", "introtext" => "x", "tv.image" => "assets/x.jpg"]);
echo "render card: calc=", substr_count($html, "stageshow/np-vinyl-calc/"), " alt=", substr_count($html, 'data-ss-alt="np-vinyl-organika,'), " braces=", substr_count($html, "{\$"), "\n";
echo "sha np_project=", hash("sha256", $npv), " res83=", hash("sha256", $rc), "\n";
echo "guards ok\n";
if (!$apply) { echo "dry run\n"; exit(0); }
file_put_contents("$bk/np_project.before.html", $npv);
file_put_contents("$bk/res83.content.before.html", $rc);
@mkdir("$bk/np-vinyl.before", 0700);
foreach (glob("$ss/np-vinyl/*") as $f) copy($f, "$bk/np-vinyl.before/" . basename($f));
// файлы: новые папки, затем старые np-vinyl перезаписать (старый URL тоже без абсолютных визитов)
foreach (["np-vinyl-calc", "np-vinyl-organika"] as $n) { mkdir("$ss/$n", 0700); foreach (glob("$src/$n/*") as $f) g(copy($f, "$ss/$n/" . basename($f)), "copy $f"); }
foreach (glob("$src/np-vinyl/*") as $f) g(copy($f, "$ss/np-vinyl/" . basename($f)), "copy $f");
$np->set("snippet", $newnp); g($np->save(), "save np_project");
$r->set("content", $new); g($r->save(), "save res83");
$modx->cacheManager->refresh();
$out = ["np_project" => hash("sha256", $modx->getObject("modChunk", ["name" => "np_project"])->get("snippet")),
  "res83" => hash("sha256", $modx->getObject("modResource", 83)->get("content"))];
file_put_contents("$bk/after.json", json_encode($out, JSON_PRETTY_PRINT));
echo json_encode($out, JSON_PRETTY_PRINT), "\n";
