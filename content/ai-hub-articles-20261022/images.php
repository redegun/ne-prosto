<?php
// task 503: set cover TVs (image + page__image--big) for hub articles whose image exists in img/
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir = __DIR__; $pub = "/home/r/redegun/ne-prosto/public_html/";
$map = json_decode(file_get_contents("$dir/map.json"), true);
@mkdir($pub."images/godnota/ii-hub", 0755);
foreach ($map as $n => [$alias, $img]) {
  $r = $modx->getObject("modResource", ["alias"=>$alias, "parent"=>2]); if (!$r) { echo "no $alias\n"; continue; }
  if (!file_exists("$dir/img/$img.jpg")) { echo "skip $n no image\n"; continue; }
  foreach (["", "-768"] as $s) copy("$dir/img/$img$s.jpg", $pub."images/godnota/ii-hub/$img$s.jpg");
  $p = "images/godnota/ii-hub/$img.jpg"; [$w,$h] = getimagesize($pub.$p);
  $r->setTVValue("image", $p);
  $r->setTVValue("page__image--big", json_encode(["sourceImg"=>["src"=>$p,"width"=>$w,"height"=>$h,"source"=>1],"crop"=>["x"=>0,"y"=>0,"width"=>$w,"height"=>$h],"targetWidth"=>0,"targetHeight"=>0]));
  echo "img $n id=",$r->id," $p {$w}x{$h}\n";
}
$modx->cacheManager->refresh();
