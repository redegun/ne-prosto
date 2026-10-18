<?php
header('Content-Type: application/json; charset=utf-8');header('Cache-Control: no-store');
if($_SERVER['REQUEST_METHOD']!=='POST'||!hash_equals('TOKEN_SHA',hash('sha256',$_SERVER['HTTP_X_NP_KEY']??''))){http_response_code(403);exit;}
define('MODX_API_MODE',true);require_once dirname(__DIR__,2).'/config.core.php';require_once MODX_CORE_PATH.'model/modx/modx.class.php';
$modx=new modX();$modx->initialize('web');
function fail($m){http_response_code(409);echo json_encode(['error'=>$m]);exit;}
if($modx->getOption('site_url')!=='https://ne-prosto.ru/')fail('Wrong site');
$p=json_decode(base64_decode('PAYLOAD_BASE64'),true);$input=json_decode(file_get_contents('php://input'),true);$action=$input['action']??'';
if(!in_array($action,['inspect','stage','publish','unpublish'],true))fail('Invalid action');
$hash=hash('sha256',$p['content']);$uri=$p['uri'];
$r=$modx->getObject('modResource',['uri'=>$uri]);
$alias=$modx->getObject('modResource',['parent'=>2,'alias'=>$p['alias']]);
if($alias&&(!$r||(int)$alias->get('id')!==(int)$r->get('id')))fail('Alias already occupied');
if($r&&((int)$r->get('parent')!==2||(int)$r->get('template')!==8||$r->get('deleted')||hash('sha256',(string)$r->get('content'))!==$hash))fail('Existing resource identity/content mismatch');
$tvs=[];
foreach($p['tvs'] as $name=>$value){$tv=$modx->getObject('modTemplateVar',['name'=>$name]);if(!$tv||!$modx->getObject('modTemplateVarTemplate',['tmplvarid'=>$tv->get('id'),'templateid'=>8]))fail('Missing TV binding '.$name);$tvs[$name]=$tv;}
function state($r,$tvs,$modx){$v=[];if($r)foreach($tvs as $n=>$tv)$v[$n]=$r->getTVValue($n);return ['resource'=>$r?$r->toArray():null,'tvs'=>$v,'parent'=>$modx->getObject('modResource',2)->toArray(),'template_sha'=>hash('sha256',$modx->getObject('modTemplate',8)->get('content'))];}
if($action==='inspect'){echo json_encode(state($r,$tvs,$modx),JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);exit;}
$modx->beginTransaction();
try{
 if($action==='stage'){
  if(!$r){$r=$modx->newObject('modDocument');$fields=$p;unset($fields['tvs']);$fields['published']=0;$fields['createdon']=time();$fields['publishedon']=0;$r->fromArray($fields,'',true,true);if(!$r->save())throw new Exception('Create failed');}
  foreach($p['tvs'] as $n=>$v)if(!$r->setTVValue($n,$v))throw new Exception('TV save failed '.$n);
 }else{
  if(!$r)throw new Exception('No staged resource');
  foreach($p['tvs'] as $n=>$v)if((string)$r->getTVValue($n)!==(string)$v)throw new Exception('TV readback mismatch '.$n);
  $r->set('published',$action==='publish'?1:0);
  if($action==='publish'&&!$r->get('publishedon'))$r->set('publishedon',time());
  if(!$r->save())throw new Exception('Publish state save failed');
 }
 $id=(int)$r->get('id');$r=$modx->getObject('modResource',$id);
 if(hash('sha256',(string)$r->get('content'))!==$hash||$r->get('uri')!==$uri||(int)$r->get('parent')!==2||(int)$r->get('template')!==8)throw new Exception('Resource readback mismatch');
 foreach($p['tvs'] as $n=>$v)if((string)$r->getTVValue($n)!==(string)$v)throw new Exception('TV readback mismatch '.$n);
 $modx->commit();$modx->cacheManager->refresh();if(function_exists('opcache_reset'))opcache_reset();
 echo json_encode(['ok'=>true,'id'=>$id,'content_sha'=>$hash,'state'=>state($r,$tvs,$modx)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
}catch(Throwable $e){$modx->rollBack();fail($e->getMessage());}
