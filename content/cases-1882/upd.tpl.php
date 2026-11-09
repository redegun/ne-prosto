<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task1882";
$new = base64_decode("@@CODE@@");
$sn = $modx->getObject("modSnippet", ["name" => "npCases"]); $cur = $sn->get("snippet");
if (hash("sha256", $cur) !== "e6eb512ea2e93efb4cf88ca8c42b78c0c25ef610e63493ca09c4e50ec0de4e01") { echo "GUARD FAIL sha ", hash("sha256", $cur), "\n"; exit(1); }
file_put_contents("$bk/npCases.v1.php", $cur);
$sn->set("snippet", $new); if (!$sn->save()) { echo "save fail\n"; exit(1); }
$modx->cacheManager->refresh(); echo "updated ", hash("sha256", $modx->getObject("modSnippet", ["name" => "npCases"])->get("snippet")), "\n";
