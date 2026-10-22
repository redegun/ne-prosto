<?php
// task 547: приём заявок всех форм и видимый e-mail -> info@ne-prosto.ru
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir=__DIR__; $mode=$argv[1]??"dry"; @mkdir("$dir/before-mail");
$NEW="info@ne-prosto.ru";
$items=[["modChunk",26,"snippet"],["modChunk",40,"snippet"],["modChunk",93,"snippet"],["modTemplate",3,"content"],["modSnippet",98,"snippet"]];
$rep=[
 "/&emailTo=`[^`]*`/" => "&emailTo=`$NEW`",
 "/\x27emailTo\x27 => \x27redegun@gmail\.com,\x27 \. /" => "\x27emailTo\x27 => ",
 "/7232308@gmail\.com/" => $NEW,
];
foreach ($items as [$c,$id,$f]) { $o=$modx->getObject($c,$id); $t=$o->get($f);
 $bf="$dir/before-mail/".strtolower(substr($c,3))."$id.txt"; if(!file_exists($bf)) file_put_contents($bf,$t);
 $n=$t; foreach($rep as $a=>$b) $n=preg_replace($a,$b,$n);
 echo "$c $id changed=".($n!==$t?"yes":"no")." gmail_left=".preg_match_all("/@gmail\.com/",$n)."\n";
 if($mode==="apply" && $n!==$t){ $o->set($f,$n); if(!$o->save()) die("save fail $c $id\n"); } }
$s=$modx->getObject("modSystemSetting","e-mail"); if(!file_exists("$dir/before-mail/setting-e-mail.txt")) file_put_contents("$dir/before-mail/setting-e-mail.txt",$s->get("value"));
echo "setting e-mail -> $NEW\n"; if($mode==="apply"){ $s->set("value",$NEW); $s->save(); $modx->cacheManager->refresh(); echo "applied\n"; }
