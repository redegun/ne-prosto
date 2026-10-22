<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir = __DIR__;
// backup
$t13=$modx->getObject("modTemplate",13); file_put_contents("$dir/template13.before.html",$t13->get("content"));
$t8=$modx->getObject("modTemplate",8); file_put_contents("$dir/template8.before.html",$t8->get("content"));
$ch=$modx->getObject("modChunk",["name"=>"np_related"]); file_put_contents("$dir/np_related.before.html",$ch->get("snippet"));
$kids=[]; foreach($modx->getCollection("modResource",["parent"=>18]) as $r) $kids[]=$r->toArray();
file_put_contents("$dir/parent18-children.before.json", json_encode($kids, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
if ($modx->getCount("modResource",["alias"=>"ii-assistent-dlya-biznesa"])) die("exists\n");
$modx->user = $modx->getObject("modUser", 1) ?: $modx->user;
$res = $modx->runProcessor("resource/create", [
 "pagetitle"=>"ИИ-ассистент для бизнеса",
 "longtitle"=>"ИИ-ассистент для бизнеса: первые ответы клиентам в мессенджерах",
 "alias"=>"ii-assistent-dlya-biznesa",
 "parent"=>18, "template"=>8, "published"=>1, "hidemenu"=>0, "searchable"=>1, "cacheable"=>1,
 "richtext"=>0, "menuindex"=>4, "class_key"=>"modDocument", "context_key"=>"web", "content_type"=>1,
 "introtext"=>"Ни одна заявка не потеряется: ассистент готовит ответ за несколько минут, менеджер одобряет его и отправляет клиенту.",
 "content"=>file_get_contents("$dir/content.html"),
 "tvs"=>true,
 "tv1"=>"ИИ-ассистент для бизнеса: первые ответы клиентам в мессенджерах — Непросто",
 "tv4"=>"Собираем первые обращения из мессенджеров в одном месте. Ассистент готовит ответ, менеджер отправляет его в один клик. Сразу видно, кто пишет впервые, а кто уже клиент.",
]);
if ($res->isError()) { print_r($res->getAllErrors()); echo $res->getMessage(),"\n"; exit(1); }
$o=$res->getObject(); echo "created id=",$o["id"]," uri=",$o["uri"]??"","\n";
$r=$modx->getObject("modResource",$o["id"]); echo "uri=",$r->uri," content_sha=",hash("sha256",$r->content)," titl=",$r->getTVValue("titl"),"\n";
$modx->cacheManager->refresh();
