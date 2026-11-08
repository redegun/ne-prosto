<?php
// task 1727: живые обложки Stageshow для lrrazbor-poisk, firmaflis и новой страницы кейса muza
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$apply = trim((string)@file_get_contents("/home/r/redegun/ne-prosto/_agent_archives/task1727/APPLY")) === "yes";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task1727"; @mkdir($bk, 0700, true);
$D = json_decode(base64_decode("@@DATA@@"), true);
function g($c, $m) { if (!$c) { echo "GUARD FAIL: $m\n"; exit(1); } }
$np = $modx->getObject("modChunk", ["name" => "np_project"]); $npv = $np->get("snippet");
g(hash("sha256", $npv) === $D["old_sha"], "np_project sha");
g(substr_count($npv, $D["anchor"]) === 1, "anchor");
$newnp = str_replace($D["anchor"], $D["add"] . $D["anchor"], $npv);
$res = [];
foreach ($D["res"] as $id => $x) { $r = $modx->getObject("modResource", (int)$id); g(hash("sha256", $r->get("content")) === $x["sha"], "res $id sha"); $res[$id] = $r; }
g($modx->getCount("modResource", ["parent" => 23, "alias" => "muza"]) === 0, "muza exists");
g((bool)$modx->getObject("modChunk", ["name" => "np_ss_case"]), "np_ss_case missing");
foreach (["np-lrrazbor", "np-flis", "np-muza"] as $n) foreach (["$n-1440.webm", "$n-1440.mp4", "$n-390.webm", "$n-390.mp4", "poster-1440.png", "poster-390.png"] as $f)
  g(is_file("/home/r/redegun/ne-prosto/public_html/assets/neprosto/stageshow/$n/$f"), "asset $n/$f");
foreach (["muza.jpg", "muza-card.jpg"] as $f) g(is_file("/home/r/redegun/ne-prosto/public_html/images/portfolio/clients/$f"), "img $f");
$pdo = $modx->getService("pdoTools");
foreach (["portfolio/vinyl-tm", "portfolio/firmaflis", "portfolio/lrrazbor-poisk", "portfolio/muza", "portfolio/iris"] as $u) {
  $html = $pdo->getChunk("@INLINE " . $newnp, ["uri" => $u, "pagetitle" => "T", "longtitle" => "", "introtext" => "x", "tv.image" => "assets/x.jpg"]);
  echo "render $u: video=", substr_count($html, "<video"), " img=", substr_count($html, "<img"), " braces=", substr_count($html, "{\$"), "\n";
}
echo "guards ok\n";
if (!$apply) { echo "dry run\n"; exit(0); }
file_put_contents("$bk/np_project.before.html", $npv);
foreach ($res as $id => $r) file_put_contents("$bk/res$id.content.before.html", $r->get("content"));
$np->set("snippet", $newnp); g($np->save(), "save np_project");
foreach ($res as $id => $r) { $r->set("content", $D["res"][$id]["call"] . "\n" . $r->get("content")); g($r->save(), "save res $id"); }
$src = $modx->getObject("modResource", 85);
$m = $modx->newObject("modDocument");
$m->fromArray(["pagetitle" => $D["muza"]["pagetitle"], "longtitle" => "", "description" => $D["muza"]["introtext"], "introtext" => $D["muza"]["introtext"],
  "alias" => $D["muza"]["alias"], "parent" => 23, "template" => 11, "published" => 1, "publishedon" => time(), "createdon" => time(), "searchable" => 1, "cacheable" => 1,
  "hidemenu" => $src->get("hidemenu"), "richtext" => 0, "content_type" => 1, "context_key" => "web", "menuindex" => 49, "content" => $D["muza"]["content"]]);
g($m->save(), "save muza");
$mid = $m->get("id");
$m->setTVValue("image", $D["muza"]["image"]);
// теги Tagger как у кейса Мерсидон (85)
$tg = 0;
if ($modx->addPackage("tagger", MODX_CORE_PATH . "components/tagger/model/")) {
  foreach ($modx->getCollection("TaggerTagResource", ["resource" => 85]) as $t) { $n = $modx->newObject("TaggerTagResource"); $n->set("tag", $t->get("tag")); $n->set("resource", $mid); if ($n->save()) $tg++; }
}
file_put_contents("$bk/created.json", json_encode(["muza_id" => $mid, "tags" => $tg]));
$modx->cacheManager->refresh();
$out = ["np_project" => hash("sha256", $modx->getObject("modChunk", ["name" => "np_project"])->get("snippet")), "muza_id" => $mid, "muza_uri" => $modx->getObject("modResource", $mid)->get("uri"), "tags" => $tg];
foreach ($res as $id => $r) $out["res$id"] = hash("sha256", $modx->getObject("modResource", (int)$id)->get("content"));
file_put_contents("$bk/after.json", json_encode($out, JSON_PRETTY_PRINT));
echo json_encode($out, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), "\n";
