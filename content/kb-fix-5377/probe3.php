<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$s = $modx->getObject("modSnippet", ["name" => "pdoSitemap"])->snippet;
foreach (explode("\n", $s) as $i => $l) if (preg_match('/hidemenu|showHidden|site_start|where|resources|searchable|cache/i', $l)) echo $i + 1, ": ", $l, "\n";
echo "== published hidden/searchable\n";
foreach ($modx->getCollection("modResource", ["published" => 1, "deleted" => 0, "context_key" => "web"]) as $r) {
  $ni = $r->getTVValue("noindex");
  if ($r->hidemenu || !$r->searchable || $ni) echo "{$r->id} {$r->uri} tpl={$r->template} hidemenu={$r->hidemenu} search={$r->searchable} ct={$r->content_type} class={$r->class_key} noindex=", $ni ? "Y" : "-", "\n";
}
$q = $modx->newQuery("modTemplateVarResource"); $q->where(["tmplvarid" => 2]);
foreach ($modx->getCollection("modTemplateVarResource", $q) as $x) echo "TV2 res={$x->contentid} val=[", $x->value, "]\n";
echo "== quotes in pagetitles\n";
foreach ($modx->getCollection("modResource", ["deleted" => 0]) as $r) if (preg_match('/["\'<>&]/', $r->pagetitle)) echo "{$r->id} {$r->pagetitle}\n";
$c = $modx->getObject("modChunk", ["name" => "page__image--big"]); echo "== page__image--big id={$c->id} sha=", hash("sha256", $c->snippet), "\n", $c->snippet, "\n";
echo "== robots raw: ", json_encode(file_get_contents("/home/r/redegun/ne-prosto/public_html/robots.txt")), "\n";
$r27 = $modx->getObject("modResource", 27); echo "== r27 content: ", json_encode($r27->content), "\n";
echo "== ls archives: ", implode(" ", scandir("/home/r/redegun/ne-prosto/_agent_archives")), "\n";
echo "== webroot top: ", implode(" ", scandir("/home/r/redegun/ne-prosto/public_html")), "\n";
