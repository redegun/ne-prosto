<?php
// task 5377: read-only разведка 2
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$root = "/home/r/redegun/ne-prosto/public_html/";
foreach ([8, 10] as $t) { $o = $modx->getObject("modTemplate", $t); echo "=== template $t sha=", hash("sha256", $o->content), "\n", $o->content, "\n"; }
echo "=== clients children of 10\n";
foreach ($modx->getCollection("modResource", ["parent" => 10, "deleted" => 0]) as $r) {
  echo "--- {$r->id} {$r->uri} pub={$r->published} tpl={$r->template} title={$r->pagetitle} longtitle={$r->longtitle} menuindex={$r->menuindex}\n";
  foreach ($r->getTemplateVars() as $tv) { $v = $r->getTVValue($tv->name); if ($v !== "" && $v !== null) echo "  TV {$tv->id} {$tv->name}: ", mb_substr(str_replace("\n", " ", $v), 0, 400), "\n"; }
}
$s = $modx->getObject("modSnippet", ["name" => "pdoSitemap"]);
echo "=== pdoSitemap static={$s->static} file={$s->static_file}\n", mb_substr($s->snippet, 0, 3000), "\n";
echo "=== logo svg\n", file_get_contents($root . "assets/portfolio/img/neprosto-logo.svg"), "\n";
echo "=== header_2019 logo part\n";
$h = $modx->getObject("modChunk", ["name" => "np_header"]);
if ($h) echo mb_substr($h->snippet, 0, 2500), "\n";
echo "=== np_article sha=", hash("sha256", $modx->getObject("modChunk", ["name" => "np_article"])->snippet), "\n", $modx->getObject("modChunk", ["name" => "np_article"])->snippet, "\n";
echo "=== np_related sha=", hash("sha256", $modx->getObject("modChunk", ["name" => "np_related"])->snippet), "\n", $modx->getObject("modChunk", ["name" => "np_related"])->snippet, "\n";
echo "=== cfg site_url line\n";
foreach (file("/home/r/redegun/ne-prosto/public_html/core/config/config.inc.php") as $l) if (preg_match('/HTTP_HOST|site_url|http_host/i', $l) && !preg_match('/pass|user/i', $l)) echo rtrim($l), "\n";
