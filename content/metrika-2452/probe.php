<?php
// task 2452: read-only probe — куда ставить Метрику, где формы, что в политике
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$re = '/ym\(|mc\.yandex|metrika|yaCounter|reachGoal|27066311|tag\.js|gtag|googletagmanager/i';
foreach (["head", "head_2019", "scripts_2019", "np_footer", "request_form"] as $n) {
  $o = $modx->getObject("modChunk", ["name" => $n]);
  $v = $o ? $o->get("snippet") : null;
  echo "===== CHUNK $n sha=", $v === null ? "NULL" : hash("sha256", $v), " len=", strlen((string)$v), "\n$v\n";
}
echo "===== TEMPLATES\n";
foreach ($modx->getCollection("modTemplate") as $t) {
  $c = $t->get("content");
  $pub = $modx->getCount("modResource", ["template" => $t->get("id"), "published" => 1, "deleted" => 0]);
  preg_match_all('/\[\[\$([a-zA-Z0-9_\-]+)|\{include\s+[\'"]?(?:chunk|file):?([^\'"\s}]+)|\$_modx->getChunk\([\'"]([^\'"]+)/', $c, $m);
  $inc = array_values(array_unique(array_filter(array_merge($m[1], $m[2], $m[3]))));
  echo $t->get("id"), "\t", $t->get("templatename"), "\tpub=$pub\t</head>=", substr_count($c, "</head>"), "\t</body>=", substr_count($c, "</body>"), "\tinc=", implode(",", $inc), "\tmetrika=", preg_match($re, $c), "\n";
}
echo "===== ELEMENTS matching metrika/goal\n";
foreach (["modChunk" => "snippet", "modSnippet" => "snippet", "modPlugin" => "plugincode", "modTemplate" => "content"] as $cls => $f)
  foreach ($modx->getCollection($cls) as $x) { $s = (string)$x->get($f); if (preg_match_all($re, $s, $mm)) echo "$cls ", $x->get("id"), " ", $x->get($cls === "modTemplate" ? "templatename" : "name"), " => ", implode(",", array_unique($mm[0])), "\n"; }
foreach ($modx->getCollection("modResource", ["deleted" => 0]) as $r) { if (preg_match_all($re, (string)$r->get("content"), $mm)) echo "res ", $r->get("id"), " ", $r->get("uri"), " => ", implode(",", array_unique($mm[0])), "\n"; }
echo "===== system settings matching\n";
foreach ($modx->getCollection("modSystemSetting") as $s) { $v = (string)$s->get("value"); if (preg_match($re, $v) || preg_match('/metrika|counter|analytics/i', $s->get("key"))) echo $s->get("key"), " = ", substr($v, 0, 200), "\n"; }
echo "===== FORM calls (AjaxForm/FormIt) in templates/chunks/resources\n";
foreach (["modChunk" => "snippet", "modTemplate" => "content"] as $cls => $f)
  foreach ($modx->getCollection($cls) as $x) { $s = (string)$x->get($f); if (preg_match_all('/\[\[!?(AjaxForm|FormIt)[^\]]*\]\]/s', $s, $mm)) foreach ($mm[0] as $call) echo "$cls ", $x->get("id"), " ", $x->get($cls === "modTemplate" ? "templatename" : "name"), ": ", preg_replace('/\s+/', ' ', $call), "\n"; }
foreach ($modx->getCollection("modResource", ["deleted" => 0]) as $r) { if (preg_match_all('/\[\[!?(AjaxForm|FormIt)[^\]]*\]\]/s', (string)$r->get("content"), $mm)) foreach ($mm[0] as $call) echo "res ", $r->get("id"), ": ", preg_replace('/\s+/', ' ', $call), "\n"; }
echo "===== ajaxform js setting / frontend\n";
foreach (["ajaxform_frontend_js", "ajaxform_frontend_css", "ajaxform_actionUrl"] as $k) echo "$k = ", $modx->getOption($k), "\n";
echo "===== POLICY 113 analytics/cookie fragments\n";
$p = $modx->getObject("modResource", 113);
if ($p) { $c = strip_tags((string)$p->get("content")); echo "editedon=", date("c", $p->get("editedon")), " len=", strlen($c), "\n"; foreach (preg_split('/(?<=[.!?])\s+/u', $c) as $sent) if (preg_match('/cookie|куки|аналит|метрик|Яндекс|счётчик|счетчик/ui', $sent)) echo " * ", trim($sent), "\n"; }
echo "===== manager log 2026-07-20..2026-09-10\n";
$q = $modx->newQuery("modManagerLog");
$q->where(["occurred:>=" => "2026-07-20 00:00:00", "occurred:<=" => "2026-09-10 23:59:59"]);
$q->sortby("occurred", "ASC"); $q->limit(200);
foreach ($modx->getCollection("modManagerLog", $q) as $l) echo $l->get("occurred"), " u=", $l->get("user"), " ", $l->get("action"), " ", $l->get("classKey"), " ", $l->get("item"), "\n";
$r1 = $modx->getObject("modResource", 1);
echo "===== res1 template=", $r1->get("template"), " editedon=", date("c", $r1->get("editedon")), "\n";
$t3 = $modx->getObject("modTemplate", 3);
echo "tpl3 exists=", $t3 ? "yes" : "no", " used_by=", $modx->getCount("modResource", ["template" => 3]), "\n";
