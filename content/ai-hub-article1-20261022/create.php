<?php
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir = __DIR__;
$kids=[]; foreach($modx->getCollection("modResource",["parent"=>2]) as $r) $kids[]=$r->toArray();
file_put_contents("$dir/parent2-children.before.json", json_encode($kids, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
$alias="kuda-propadayut-zayavki-iz-messendzherov";
if ($modx->getCount("modResource",["alias"=>$alias])) die("exists\n");
$img="images/godnota/ii-zayavki-messendzhery.jpg";
$dst="/home/r/redegun/ne-prosto/public_html/".$img;
if (!file_exists($dst)) copy("$dir/ii-zayavki-messendzhery.jpg",$dst);
$modx->user = $modx->getObject("modUser", 1) ?: $modx->user;
$desc="Почему теряются заявки из мессенджеров, пока менеджер на звонке или встрече, как это заметить и как не терять клиентов: один список обращений, срок первого ответа, ассистент с одобрением менеджера.";
$res = $modx->runProcessor("resource/create", [
 "pagetitle"=>"Куда пропадают заявки из мессенджеров, пока менеджер занят",
 "alias"=>$alias, "description"=>$desc,
 "parent"=>2, "template"=>8, "published"=>1, "hidemenu"=>0, "searchable"=>1, "cacheable"=>1,
 "richtext"=>1, "menuindex"=>12, "class_key"=>"modDocument", "context_key"=>"web", "content_type"=>1,
 "introtext"=>"Где теряются заявки из мессенджеров, когда менеджер занят, как это заметить и что сделать, чтобы клиенты не уходили к тем, кто ответил первым.",
 "content"=>file_get_contents("$dir/content.html"),
 "tvs"=>true,
 "tv1"=>"Куда пропадают заявки из мессенджеров и как не терять клиентов — Непросто",
 "tv4"=>$desc,
 "tv5"=>$img,
 "tv11"=>"0.7", "tv12"=>"weekly",
 "tv13"=>json_encode(["sourceImg"=>["src"=>$img,"width"=>1800,"height"=>1300,"source"=>1],"crop"=>["x"=>0,"y"=>0,"width"=>1800,"height"=>1300],"targetWidth"=>0,"targetHeight"=>0]),
]);
if ($res->isError()) { print_r($res->getAllErrors()); echo $res->getMessage(),"\n"; exit(1); }
$o=$res->getObject(); $r=$modx->getObject("modResource",$o["id"]);
echo "created id=",$r->id," uri=",$r->uri," pub=",$r->published," image=",$r->getTVValue("image")," big=",$r->getTVValue("page__image--big"),"\n";
file_put_contents("$dir/resource.after.json", json_encode($r->toArray(), JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
$modx->cacheManager->refresh();
