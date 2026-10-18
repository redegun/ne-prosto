<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD']!=='POST' || !hash_equals('TOKEN_SHA',hash('sha256',$_SERVER['HTTP_X_STANKIN_KEY']??''))) {http_response_code(403);exit;}
define('MODX_API_MODE',true);
require_once dirname(__DIR__,2).'/config.core.php';
require_once MODX_CORE_PATH.'model/modx/modx.class.php';
$modx=new modX();$modx->initialize('web');
$r=$modx->getObject('modResource',100);
$t=$modx->getObject('modTemplate',15);
if(!$r || !$t || $r->get('alias')!=='poezd-stankin' || (int)$r->get('template')!==15){http_response_code(409);exit;}
$users=$modx->getCollection('modResource',['template'=>15]);
if(count($users)!==1){http_response_code(409);echo json_encode(['error'=>'Template is shared']);exit;}
$spec=json_decode(base64_decode('SPEC_BASE64'),true);
$in=json_decode(file_get_contents('php://input'),true);
$beforeR=$r->get('content');$beforeT=$t->get('content');
if(($in['action']??'')==='publish'){
 foreach([['resource',$beforeR],['template',$beforeT]] as $row){
  $sha=hash('sha256',$row[1]);$entry=$spec[$row[0]];
  if(!in_array($sha,[$entry['expected'],$entry['target']],true) ||
     hash('sha256',$entry['content'])!==$entry['target']){
   http_response_code(409);echo json_encode(['error'=>'Content changed','field'=>$row[0]]);exit;
  }
 }
 try{
  $r->set('content',$spec['resource']['content']);
  if(!$r->save()){throw new Exception('Resource save failed');}
  $t->set('content',$spec['template']['content']);
  if(!$t->save()){throw new Exception('Template save failed');}
  $modx->cacheManager->refresh();
 }catch(Throwable $e){
  $r->set('content',$beforeR);$r->save();
  $t->set('content',$beforeT);$t->save();
  $modx->cacheManager->refresh();
  http_response_code(500);echo json_encode(['error'=>'Save failed; previous values restored']);exit;
 }
}
echo json_encode([
 'resource'=>$r->toArray(),'template'=>$t->toArray(),
 'resource_sha'=>hash('sha256',$r->get('content')),
 'template_sha'=>hash('sha256',$t->get('content'))
],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
