<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$t = $modx->getObject("modTemplate", 14); echo "=== tpl14 sha=", hash("sha256", $t->content), "\n", $t->content, "\n";
foreach ($modx->getCollection("modResource", ["template" => 14, "deleted" => 0]) as $r) {
  echo "=== res {$r->id} {$r->uri} pub={$r->published} title={$r->pagetitle} content_len=", strlen($r->content), " img=", substr_count($r->content, "<img"), " emptyalt=", preg_match_all('/<img[^>]*alt=(""|\'\')/', $r->content), "\n";
  foreach ($r->getTemplateVars() as $tv) { $v = (string)$r->getTVValue($tv->name); if ($v !== "") echo "  TV {$tv->id} {$tv->name} type={$tv->type}: ", mb_substr(str_replace("\n", " ", $v), 0, 200), "\n"; }
  echo "  content head: ", mb_substr(str_replace("\n", " ", $r->content), 0, 500), "\n";
}
