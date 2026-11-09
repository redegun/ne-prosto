<?php
// task 1882: сниппет npCases + вызов в карточке np_project + [[!npCases]] в content кейсов merci(85) и kppf(84)
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task1882"; @mkdir($bk, 0700, true);
$apply = trim((string)@file_get_contents("$bk/APPLY")) === "yes";
$D = json_decode(base64_decode("@@DATA@@"), true);
function g($c, $m) { if (!$c) { echo "GUARD FAIL: $m\n"; exit(1); } }
// guards
$np = $modx->getObject("modChunk", ["name" => "np_project"]); $npv = $np->get("snippet");
g(hash("sha256", $npv) === $D["np_sha"], "np_project sha " . hash("sha256", $npv));
g(substr_count($npv, $D["np_anchor"]) === 1, "np anchor");
g(strpos($npv, "npCases") === false, "np already");
$res = [];
foreach ($D["res"] as $id => $r) {
  $o = $modx->getObject("modResource", (int)$id); $c = $o->get("content");
  g($o->get("uri") === $r["uri"], "res$id uri");
  g(hash("sha256", $c) === $r["sha"], "res$id sha " . hash("sha256", $c));
  g(substr_count($c, $r["anchor"]) === 1, "res$id anchor");
  g(strpos($c, "npCases") === false, "res$id already");
  $res[$id] = [$o, $c, $r];
}
$sn = $modx->getObject("modSnippet", ["name" => "npCases"]);
g(!$sn, "snippet exists");
foreach (["merci", "kppf"] as $s) g(is_file("/home/r/redegun/ne-prosto/np-cases/$s.json"), "json $s");
g(is_file("/home/r/redegun/ne-prosto/public_html/assets/neprosto/cases/cases.css"), "css");
$newnp = str_replace($D["np_anchor"], $D["np_anchor"] . $D["np_call"], $npv);
// пробный рендер: временный сниппет в памяти не создать — проверяем код через eval-обёртку
$code = $D["snippet"];
$fn = function ($scriptProperties) use ($modx, $code) { return eval("?>" . $code); };
foreach (["portfolio/merci", "portfolio/kppf", "portfolio/iris"] as $u) {
  $c = $fn(["mode" => "card", "uri" => $u]); $p = $fn(["mode" => "case", "uri" => $u]);
  echo "render $u: card=", strlen($c), " tags=", substr_count($c, "<li>"), " case=", strlen($p), " items=", substr_count($p, "<details"), "\n";
}
echo "guards ok\n";
if (!$apply) { echo "dry run\n"; exit(0); }
file_put_contents("$bk/np_project.before.html", $npv);
foreach ($res as $id => $x) file_put_contents("$bk/res$id.content.before.html", $x[1]);
$sn = $modx->newObject("modSnippet");
$sn->set("name", "npCases"); $sn->set("description", "#1882 Что сделали: блок кейса и теги карточки, данные ~/ne-prosto/np-cases/*.json");
$sn->set("snippet", preg_replace('~^<\?php\s*~', '', $code)); $sn->set("category", 0);
g($sn->save(), "save snippet");
$np->set("snippet", $newnp); g($np->save(), "save np_project");
foreach ($res as $id => $x) { $x[0]->set("content", str_replace($x[2]["anchor"], $D["res_call"] . $x[2]["anchor"], $x[1])); g($x[0]->save(), "save res$id"); }
$modx->cacheManager->refresh();
$out = ["np_project" => hash("sha256", $modx->getObject("modChunk", ["name" => "np_project"])->get("snippet")),
  "snippet_id" => $modx->getObject("modSnippet", ["name" => "npCases"])->get("id")];
foreach ($res as $id => $x) $out["res$id"] = hash("sha256", $modx->getObject("modResource", (int)$id)->get("content"));
file_put_contents("$bk/after.json", json_encode($out, JSON_PRETTY_PRINT));
@unlink("$bk/APPLY");
echo json_encode($out, JSON_PRETTY_PRINT), "\n";
