<?php
// task 5377: read-only разведка
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$root = "/home/r/redegun/ne-prosto/public_html/";
echo "== files\n";
foreach (["robots.txt", "favicon.ico", "favicon.png", "favicon.svg", "apple-touch-icon.png", "sitemap.xml", ".htaccess"] as $f) echo $f, ": ", file_exists($root.$f) ? "exists ".filesize($root.$f) : "no", "\n";
echo "== favicon-like assets\n";
$it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root."assets", FilesystemIterator::SKIP_DOTS));
$n = 0;
foreach ($it as $f) { $p = $f->getPathname(); if (preg_match('#(favicon|apple-touch|/icon[^/]*\.(png|ico|svg)$|logo[^/]*\.(svg|png)$)#i', $p)) { echo substr($p, strlen($root)), " ", $f->getSize(), "\n"; if (++$n > 60) break; } }
echo "== htaccess favicon/robots/sitemap lines\n";
foreach (file($root.".htaccess") as $i => $l) if (preg_match('/favicon|robots|sitemap|index\.php|RewriteRule/i', $l)) echo $i+1, ": ", rtrim($l), "\n";
echo "== resources by alias\n";
foreach ($modx->getCollection("modResource", ["alias:IN" => ["sitemap", "sitemap.xml", "robots", "robots.txt", "404"]]) as $r) {
  echo $r->id, " ", $r->alias, " uri=", $r->uri, " tpl=", $r->template, " pub=", $r->published, " search=", $r->searchable, " ct=", $r->content_type, " cache=", $r->cacheable, "\n  content: ", substr($r->content, 0, 600), "\n";
}
$r1 = $modx->getObject("modResource", 1);
echo "== res1 pub=", $r1->published, " search=", $r1->searchable, " hidemenu=", $r1->hidemenu, " deleted=", $r1->deleted, " tpl=", $r1->template, " uri=", $r1->uri, "\n";
echo "site_start=", $modx->getOption("site_start"), " error_page=", $modx->getOption("error_page"), " site_url=", $modx->getOption("site_url"), "\n";
$r17 = $modx->getObject("modResource", 17);
echo "== res17 alias=", $r17->alias, " tpl=", $r17->template, " pub=", $r17->published, " search=", $r17->searchable, " noindexTV=[", $r17->getTVValue("noindex"), "]\n";
$tv = $modx->getObject("modTemplateVar", ["name" => "noindex"]);
echo "tv noindex id=", $tv->id, " type=", $tv->type, " elements=", $tv->elements, " default=", $tv->default_text, "\n";
$tt = $modx->getObject("modTemplateVarTemplate", ["tmplvarid" => $tv->id, "templateid" => $r17->template]);
echo "tv assigned to tpl ", $r17->template, ": ", $tt ? "yes" : "no", "\n";
echo "== chunks head / head_2019\n";
foreach (["head", "head_2019"] as $c) { $o = $modx->getObject("modChunk", ["name" => $c]); $v = $o->get("snippet"); echo "--- $c sha=", hash("sha256", $v), " len=", strlen($v), "\n", $v, "\n"; }
echo "== templates usage\n";
foreach ($modx->getCollection("modTemplate") as $t) {
  $cnt = $modx->getCount("modResource", ["template" => $t->id, "published" => 1, "deleted" => 0]);
  $c = $t->get("content");
  echo $t->id, " ", $t->templatename, " pub=", $cnt, " head=", (strpos($c, "[[\$head_2019") !== false ? "head_2019" : (strpos($c, "[[\$head") !== false ? "head" : (strpos($c, "head") !== false ? "other" : "-"))), " len=", strlen($c), "\n";
}
echo "== search strings in templates/chunks/snippets/resources\n";
$needles = ["Пвл", "Графическая дизайнер", "article__img", 'alt=""', "alt=''"];
foreach (["modTemplate" => "content", "modChunk" => "snippet", "modSnippet" => "snippet", "modPlugin" => "plugincode"] as $cls => $fld) {
  foreach ($modx->getCollection($cls) as $o) {
    $v = (string)$o->get($fld);
    $name = $cls === "modTemplate" ? $o->templatename : $o->name;
    foreach ($needles as $nd) {
      $p = 0; $k = 0;
      while (($p = mb_strpos($v, $nd, $p)) !== false && $k < 4) { echo "$cls#{$o->id} $name [$nd]: ", str_replace("\n", " ", mb_substr($v, max(0, $p - 160), 330)), "\n"; $p += mb_strlen($nd); $k++; }
    }
  }
}
foreach ($modx->getCollection("modResource", ["deleted" => 0]) as $r) {
  foreach (["Пвл", "Графическая дизайнер"] as $nd) { $v = $r->content; if (($p = mb_strpos($v, $nd)) !== false) echo "res#{$r->id} {$r->uri} [$nd]: ", str_replace("\n", " ", mb_substr($v, max(0, $p - 120), 260)), "\n"; }
}
$q = $modx->newQuery("modTemplateVarResource"); $q->where(["value:LIKE" => "%Пвл%"]); foreach ($modx->getCollection("modTemplateVarResource", $q) as $x) echo "TVval tv=", $x->tmplvarid, " res=", $x->contentid, " ", mb_substr($x->value, 0, 300), "\n";
$q = $modx->newQuery("modTemplateVarResource"); $q->where(["value:LIKE" => "%Графическая дизайнер%"]); foreach ($modx->getCollection("modTemplateVarResource", $q) as $x) echo "TVval tv=", $x->tmplvarid, " res=", $x->contentid, " ", mb_substr($x->value, 0, 300), "\n";
