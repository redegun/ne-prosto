<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$root = "/home/r/redegun/ne-prosto/public_html/";
$out = [];
foreach ([62, 63, 64, 65, 67, 68, 69] as $id) {
  $r = $modx->getObject("modResource", $id);
  preg_match_all('/<img\b[^>]*>/', $r->content, $m);
  foreach ($m[0] as $i => $tag) {
    preg_match('/src="([^"]+)"/', $tag, $s); preg_match('/class="([^"]*)"/', $tag, $c);
    $f = $root . ltrim($s[1] ?? "", "/"); $sz = @getimagesize($f);
    $out[] = ["id" => $id, "i" => $i, "src" => $s[1] ?? "", "class" => $c[1] ?? "", "w" => $sz[0] ?? 0, "h" => $sz[1] ?? 0, "tag" => $tag];
  }
  $out[] = ["id" => $id, "sha" => hash("sha256", $r->content)];
}
echo json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
