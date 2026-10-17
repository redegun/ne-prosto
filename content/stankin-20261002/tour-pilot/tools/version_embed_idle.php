<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD']!=='POST' || !hash_equals('TOKEN_SHA',hash('sha256',$_SERVER['HTTP_X_STANKIN_KEY']??''))) {http_response_code(403);exit;}
define('MODX_API_MODE',true);
require_once dirname(__DIR__,2).'/config.core.php';
require_once MODX_CORE_PATH.'model/modx/modx.class.php';
$modx=new modX();$modx->initialize('web');
$r=$modx->getObject('modResource',100);
if(!$r || $r->get('alias')!=='poezd-stankin'){http_response_code(409);exit;}
$before=$r->get('content');$in=json_decode(file_get_contents('php://input'),true);
if(($in['action']??'')==='version'){
 $sha=hash('sha256',$before);
 if($sha!=='TARGET_SHA'){
  if($sha!=='EXPECTED_SHA'){http_response_code(409);echo json_encode(['error'=>'Content changed']);exit;}
  $next=$before;
  foreach(['embed.css','embed.js'] as $name){
   $old='/images/portfolio/stankin/tour-20261008/'.$name.'?v=20261018-wide1"';
   if(substr_count($next,$old)!==1){http_response_code(422);exit;}
   $next=str_replace($old,'/images/portfolio/stankin/tour-20261008/'.$name.'?v=20261018-idle1"',$next);
  }
  if(hash('sha256',$next)!=='TARGET_SHA'){http_response_code(422);exit;}
  $r->set('content',$next);if(!$r->save()){http_response_code(500);exit;}
 }
 $modx->cacheManager->refresh();
}
$r=$modx->getObject('modResource',100);
echo json_encode(['resource'=>$r->toArray(),'sha256'=>hash('sha256',$r->get('content'))],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
