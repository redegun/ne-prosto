<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir=__DIR__;
$c=$modx->getObject("modChunk",["name"=>"np_related"]); $cc=$c->get("snippet");
if (hash("sha256",$cc)!=="98ce88ef9eb809b06b8e043b3cf58372526f52023625fcfc2c8682997de0e109") die("guard\n");
$orig=file_get_contents("$dir/np_related.before.html");
// task510: карточка ИИ-ассистента (103) скрыта, пока нет иллюстрации
$new="{if \$id != 103}\n".$orig."\n{/if}";
$c->set("snippet",$new); if(!$c->save()) die("save\n");
$modx->cacheManager->refresh();
file_put_contents("$dir/np_related.after.html",$new);
echo "ok ",hash("sha256",$new),"\n";
