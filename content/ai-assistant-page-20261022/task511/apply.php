<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir=__DIR__; $mode=$argv[1] ?? "dry";
$B="/assets/neprosto/design-20261018/services/";
// template 8: hero for 103
$t=$modx->getObject("modTemplate",8); $c=$t->get("content");
if (!file_exists("$dir/template8.before.html")) file_put_contents("$dir/template8.before.html",$c);
if (hash("sha256",$c)!=="3e6980dc41290d3e379be39fafe1fac9dbddd554f7f713f9a9cd39ed9fe1ee95") die("t8 guard\n");
$o="</figure>`]]</div>"; if (substr_count($c,$o)!==1) die("t8 needle\n");
$fig="[[*id:is=`103`:then=`<figure class=\"np-service-hero-art\"><img class=\"\" src=\"{$B}ai-960.webp\" srcset=\"{$B}ai-480.webp 480w, {$B}ai-960.webp 960w, {$B}ai-1440.webp 1440w\" sizes=\"(max-width: 700px) 90vw, 45vw\" width=\"1440\" height=\"1080\" alt=\"\" loading=\"eager\" decoding=\"async\"></figure>`]]";
$n8=str_replace($o,"</figure>`]]\n".$fig."</div>",$c);
// np_related: show 103 with art
$ch=$modx->getObject("modChunk",["name"=>"np_related"]); $cc=$ch->get("snippet");
if (!file_exists("$dir/np_related.before.html")) file_put_contents("$dir/np_related.before.html",$cc);
if (hash("sha256",$cc)!=="ff8c39d869f10a79fd1f18666a8364d18f62bba4fe38808c8c0cc766f36e1459") die("chunk guard\n");
if (strpos($cc,"{if \$id != 103}\n")!==0 || substr($cc,-6)!=="\n{/if}") die("chunk wrap\n");
$ncc=substr($cc,strlen("{if \$id != 103}\n"),-strlen("\n\n{/if}"));
$o2="{if \$id == 13}{set \$art = 'social'}{/if}\n"; if (substr_count($ncc,$o2)!==1) die("chunk needle\n");
$ncc=str_replace($o2,$o2."{if \$id == 103}{set \$art = 'ai'}{/if}\n",$ncc);
// head_2019: og:image for 103
$h=$modx->getObject("modChunk",["name"=>"head_2019"]); $hc=$h->get("snippet");
if (!file_exists("$dir/head_2019.before.html")) file_put_contents("$dir/head_2019.before.html",$hc);
$o3=":else=`[[++site_url]][[*image]]`]]"; if (substr_count($hc,$o3)!==1) die("head needle\n");
$nhc=str_replace($o3,":else=`[[*id:is=`103`:then=`https://ne-prosto.ru{$B}ai-1440.webp`:else=`[[++site_url]][[*image]]`]]`]]",$hc);
file_put_contents("$dir/template8.after.html",$n8); file_put_contents("$dir/np_related.after.html",$ncc); file_put_contents("$dir/head_2019.after.html",$nhc);
echo "t8 ",hash("sha256",$n8),"\nnp_related ",hash("sha256",$ncc),"\nhead_2019 ",hash("sha256",$nhc)," (before ",hash("sha256",$hc),")\n";
if ($mode!=="apply") exit("dry ok\n");
$pub="/home/r/redegun/ne-prosto/public_html".$B;
foreach ([480,960,1440] as $w){ $f="ai-$w.webp"; if (file_exists($pub.$f)) die("$f exists\n"); copy("$dir/$f",$pub.$f); chmod($pub.$f,0644); }
$t->set("content",$n8); $t->save(); $ch->set("snippet",$ncc); $ch->save(); $h->set("snippet",$nhc); $h->save();
$modx->cacheManager->refresh();
echo "applied; readback t8 ",hash("sha256",$modx->getObject("modTemplate",8)->get("content")),"\n";
