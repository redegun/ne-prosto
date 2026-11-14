<?php
// task 2452: read-only probe 2 — формы в статьях/вакансиях, политика, журнал менеджера
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
foreach (["npArticleCta"] as $n) {
  $o = $modx->getObject("modSnippet", ["name" => $n]);
  $v = $o ? $o->get("snippet") : "";
  echo "===== SNIPPET $n len=", strlen($v), "\n";
  foreach (preg_split('/\n/', $v) as $i => $l) if (preg_match('/AjaxForm|FormIt|frontend_js|runSnippet|form/i', $l)) echo ($i + 1), ": ", substr(trim($l), 0, 300), "\n";
}
$o = $modx->getObject("modChunk", ["name" => "jobs__item"]);
echo "===== jobs__item\n";
foreach (preg_split('/\n/', $o->get("snippet")) as $l) if (preg_match('/frontend_js|AjaxForm|&form/i', $l)) echo trim($l), "\n";
echo "===== which templates are used by vacancies / articles\n";
foreach ([14, 2, 104, 122, 7, 1, 113, 114] as $id) { $r = $modx->getObject("modResource", $id); if ($r) echo $id, " ", $r->get("uri"), " tpl=", $r->get("template"), " pub=", $r->get("published"), "\n"; }
echo "===== POLICY 113\n";
$p = $modx->getObject("modResource", 113);
echo "editedon=", $p->get("editedon"), " sha=", hash("sha256", (string)$p->get("content")), "\n";
echo $p->get("content"), "\n";
echo "===== manager log 2026-07-20..2026-09-10\n";
$q = $modx->newQuery("modManagerLog");
$q->where(["occurred:>=" => "2026-07-20 00:00:00", "occurred:<=" => "2026-09-10 23:59:59"]);
$q->sortby("occurred", "ASC"); $q->limit(300);
foreach ($modx->getCollection("modManagerLog", $q) as $l) echo $l->get("occurred"), " u=", $l->get("user"), " ", $l->get("action"), " ", $l->get("classKey"), " ", $l->get("item"), "\n";
$r1 = $modx->getObject("modResource", 1);
echo "===== res1 template=", $r1->get("template"), " editedon=", $r1->get("editedon"), "\n";
