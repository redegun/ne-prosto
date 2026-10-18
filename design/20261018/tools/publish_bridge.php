<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if($_SERVER['REQUEST_METHOD']!=='POST'||!hash_equals('TOKEN_SHA',hash('sha256',$_SERVER['HTTP_X_NP_KEY']??''))){http_response_code(403);exit;}
define('MODX_API_MODE',true);
require_once dirname(__DIR__,2).'/config.core.php';
require_once MODX_CORE_PATH.'model/modx/modx.class.php';
$modx=new modX();$modx->initialize('web');
function fail($message){http_response_code(409);echo json_encode(['error'=>$message]);exit;}
if($modx->getOption('site_url')!=='https://ne-prosto.ru/')fail('Wrong site');
$input=json_decode(file_get_contents('php://input'),true);
if(!is_array($input)||!in_array($input['action']??'', ['inspect','apply'],true))fail('Invalid action');
$allowed=['modTemplate'=>'content','modChunk'=>'snippet','modResource'=>'content','modTemplateVarResource'=>'value'];
$changes=$input['changes']??[];
if(count($changes)<1||count($changes)>50)fail('Invalid count');
$rows=[];$objects=[];
foreach($changes as $i=>$c){
 $class=$c['type']??'';$field=$c['field']??'';
 if(!isset($allowed[$class])||$allowed[$class]!==$field)fail('Invalid type/field');
 if(!$c['id']&&($class!=='modChunk'||!preg_match('/^np_[a-z_]+$/',$c['name'])))fail('Invalid new object');
 $o=$modx->getObject($class,$c['id']?(int)$c['id']:['name'=>$c['name']]);
 if($c['id']&&!$o)fail('Missing object '.$i);
 if($class==='modChunk'&&$o&&$o->get('name')!==$c['name'])fail('Chunk identity mismatch');
 $value=$o?(string)$o->get($field):null;
 $hash=$value===null?null:hash('sha256',$value);
 if($hash!==$c['expected']&&$hash!==$c['target'])fail('Source changed '.$class.' '.($c['id']?:$c['name']));
 if(!is_string($c['content'])||hash('sha256',$c['content'])!==$c['target'])fail('Payload hash mismatch');
 $rows[]=['type'=>$class,'id'=>$o?$o->get('id'):null,'name'=>$c['name'],'field'=>$field,'value'=>$value,'hash'=>$hash,'object'=>$o?$o->toArray():null];
 $objects[]=$o;
}
if($input['action']==='inspect'){echo json_encode(['site_url'=>$modx->getOption('site_url'),'before'=>$rows],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);exit;}
$written=[];
try{
 foreach($changes as $i=>$c){
  if($rows[$i]['hash']===$c['target'])continue;
  $o=$objects[$i];
  if(!$o){$o=$modx->newObject($c['type']);$o->set('name',$c['name']);$o->set('description','Neprosto editorial design 2026-10-18');}
  $o->set($c['field'],$c['content']);
  if(!$o->save())throw new Exception('Save failed '.$i);
  $written[]=$i;$objects[$i]=$o;
 }
 $result=[];
 foreach($changes as $i=>$c){
  $o=$modx->getObject($c['type'],(int)$objects[$i]->get('id'));
  $hash=hash('sha256',(string)$o->get($c['field']));
  if($hash!==$c['target'])throw new Exception('Readback mismatch '.$i);
  $result[]=['type'=>$c['type'],'id'=>$o->get('id'),'hash'=>$hash];
 }
 $modx->cacheManager->refresh();
 if(function_exists('opcache_reset'))opcache_reset();
 echo json_encode(['ok'=>true,'updated'=>count($written),'readback'=>$result],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
}catch(Throwable $e){
 foreach(array_reverse($written) as $i){
  if($rows[$i]['value']!==null){$objects[$i]->set($changes[$i]['field'],$rows[$i]['value']);$objects[$i]->save();}
 }
 $modx->cacheManager->refresh();
 fail($e->getMessage().' — previous field values restored');
}
