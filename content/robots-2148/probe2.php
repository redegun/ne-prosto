<?php
// task 2148: read-only probe — TV noindex
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$tv = $modx->getObject("modTemplateVar", 2);
foreach (["name", "caption", "type", "elements", "default_text", "display", "output_properties", "input_properties", "description"] as $f) {
  $v = $tv->get($f);
  echo "$f: ", is_array($v) ? json_encode($v, JSON_UNESCAPED_UNICODE) : $v, "\n";
}
echo "===== templates bound\n";
foreach ($modx->getCollection("modTemplateVarTemplate", ["tmplvarid" => 2]) as $l) echo $l->get("templateid"), " ";
echo "\n===== values\n";
$q = $modx->newQuery("modTemplateVarResource", ["tmplvarid" => 2]);
foreach ($modx->getCollection("modTemplateVarResource", $q) as $v) {
  $r = $modx->getObject("modResource", $v->get("contentid"));
  echo $v->get("contentid"), "\t", $r ? $r->get("uri") : "?", "\tpub=", $r ? $r->get("published") : "?", "\ttpl=", $r ? $r->get("template") : "?", "\tval=", json_encode($v->get("value"), JSON_UNESCAPED_UNICODE), "\n";
}
echo "===== rendered for sample\n";
foreach ([1, 122, 2, 113] as $id) {
  $r = $modx->getObject("modResource", $id);
  if (!$r) continue;
  echo $id, " ", $r->get("uri"), " -> ", json_encode($r->getTVValue("noindex"), JSON_UNESCAPED_UNICODE), "\n";
}
echo "===== all published resources (id uri tpl ct)\n";
$c = $modx->newQuery("modResource", ["published" => 1, "deleted" => 0]);
$c->sortby("id");
foreach ($modx->getCollection("modResource", $c) as $r) echo $r->get("id"), "\t", $r->get("uri"), "\t", $r->get("template"), "\t", $r->get("content_type"), "\t", $r->get("class_key"), "\n";
