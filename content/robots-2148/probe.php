<?php
// task 2148: read-only probe — где head, где robots/noindex
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$out = [];
foreach (["head", "head_2019"] as $n) {
  $o = $modx->getObject("modChunk", ["name" => $n]);
  $v = $o ? $o->get("snippet") : null;
  $out["chunk_$n"] = ["sha" => $v === null ? null : hash("sha256", $v), "len" => strlen((string)$v)];
  echo "===== CHUNK $n\n$v\n";
}
echo "===== TEMPLATES\n";
foreach ($modx->getCollection("modTemplate") as $t) {
  $c = $t->get("content");
  $cnt = $modx->getCount("modResource", ["template" => $t->get("id")]);
  $pub = $modx->getCount("modResource", ["template" => $t->get("id"), "published" => 1, "deleted" => 0]);
  $h = [];
  if (strpos($c, "head_2019") !== false) $h[] = "head_2019";
  if (preg_match('/\$head[^_]|\{include .file:chunks\/head|\[\[\$head[\]?]|\$head\b(?!_)/', $c)) $h[] = "head";
  $rob = preg_match_all('/robots|noindex|nofollow/i', $c);
  echo $t->get("id"), "\t", $t->get("templatename"), "\tres=$cnt pub=$pub\thead=", implode(",", $h), "\trobots=$rob\t<head>=", substr_count($c, "<head"), "\n";
}
echo "===== CHUNKS with robots/noindex\n";
foreach ($modx->getCollection("modChunk") as $ch) {
  $s = $ch->get("snippet");
  if (preg_match('/robots|noindex/i', $s)) echo $ch->get("name"), "\n";
}
echo "===== SNIPPETS/PLUGINS with robots/noindex\n";
foreach (["modSnippet", "modPlugin"] as $cls) foreach ($modx->getCollection($cls) as $x) {
  $s = $x->get($cls === "modSnippet" ? "snippet" : "plugincode");
  if (preg_match('/robots|noindex|X-Robots/i', $s)) echo $cls, " ", $x->get("name"), "\n";
}
echo "===== RESOURCES with robots/noindex in content\n";
foreach ($modx->getCollection("modResource", ["deleted" => 0]) as $r) {
  if (preg_match('/robots|noindex/i', (string)$r->get("content"))) echo $r->get("id"), " ", $r->get("uri"), "\n";
}
echo "===== TV names\n";
foreach ($modx->getCollection("modTemplateVar") as $tv) {
  if (preg_match('/robot|index|seo|meta/i', $tv->get("name") . " " . $tv->get("caption"))) echo $tv->get("id"), " ", $tv->get("name"), " | ", $tv->get("caption"), "\n";
}
echo "===== published non-searchable / hidemenu stats\n";
foreach ($modx->getCollection("modResource", ["published" => 1, "deleted" => 0, "searchable" => 0]) as $r) echo "nonsearchable ", $r->get("id"), " ", $r->get("uri"), " tpl=", $r->get("template"), " ct=", $r->get("content_type"), "\n";
echo "===== htaccess robots\n";
foreach (preg_split('/\n/', (string)@file_get_contents("/home/r/redegun/ne-prosto/public_html/.htaccess")) as $i => $l) if (preg_match('/robots|noindex/i', $l)) echo ($i + 1), ": ", $l, "\n";
echo "===== robots.txt\n", @file_get_contents("/home/r/redegun/ne-prosto/public_html/robots.txt"), "\n";
echo json_encode($out), "\n";
