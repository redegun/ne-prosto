<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD']!=='POST' || !hash_equals('TOKEN_SHA',hash('sha256',$_SERVER['HTTP_X_STANKIN_KEY']??''))) {http_response_code(403);exit;}
define('MODX_API_MODE',true);
require_once dirname(__DIR__,2).'/config.core.php';
require_once MODX_CORE_PATH.'model/modx/modx.class.php';
$modx=new modX();$modx->initialize('web');
$r=$modx->getObject('modResource',100);
if(!$r){http_response_code(409);exit;}
$t=$modx->getObject('modTemplate',(int)$r->get('template'));
if(!$r || !$t || $r->get('alias')!=='poezd-stankin'){http_response_code(409);echo json_encode(['error'=>'Wrong resource']);exit;}
$spec=json_decode(base64_decode('SPEC_BASE64'),true);
$in=json_decode(file_get_contents('php://input'),true);
$beforeR=$r->get('content');$beforeTemplate=(int)$r->get('template');
if(($in['action']??'')==='publish'){
 $sha=hash('sha256',$beforeR);
 if(!in_array($sha,[$spec['resource']['expected'],$spec['resource']['target']],true) ||
    hash('sha256',$spec['resource']['content'])!==$spec['resource']['target'] ||
    hash('sha256',$spec['template']['content'])!==$spec['template']['target']){
  http_response_code(409);echo json_encode(['error'=>'Content changed']);exit;
 }
 $currentTemplateSha=hash('sha256',$t->get('content'));
 if(!in_array($currentTemplateSha,[$spec['template']['expected'],$spec['template']['target']],true)){
  http_response_code(409);echo json_encode(['error'=>'Source template changed']);exit;
 }
 $name='STANKIN full-width case 20261018';
 $next=$modx->getObject('modTemplate',['templatename'=>$name]);
 if($next){
  if(hash('sha256',$next->get('content'))!==$spec['template']['target']){
   http_response_code(409);echo json_encode(['error'=>'Existing target template changed']);exit;
  }
  foreach($modx->getCollection('modResource',['template'=>$next->get('id')]) as $user){
   if((int)$user->get('id')!==100){http_response_code(409);echo json_encode(['error'=>'Target template is shared']);exit;}
  }
 }else{
  $next=$modx->newObject('modTemplate');
  $next->fromArray(['templatename'=>$name,'description'=>'Full-width cover and immediate 3D viewer for STANKIN resource 100','content'=>$spec['template']['content'],'category'=>$t->get('category')]);
  if(!$next->save()){http_response_code(500);echo json_encode(['error'=>'Template creation failed']);exit;}
 }
 // Preserve the original template's TV bindings in the new isolated template.
 foreach($modx->getCollection('modTemplateVarTemplate',['templateid'=>15]) as $binding){
  $where=['tmplvarid'=>$binding->get('tmplvarid'),'templateid'=>$next->get('id')];
  if(!$modx->getObject('modTemplateVarTemplate',$where)){
   $copy=$modx->newObject('modTemplateVarTemplate');
   $copy->fromArray(array_merge($where,['rank'=>$binding->get('rank')]));
   if(!$copy->save()){http_response_code(500);echo json_encode(['error'=>'TV binding copy failed']);exit;}
  }
 }
 try{
  $r->set('content',$spec['resource']['content']);$r->set('template',$next->get('id'));
  if(!$r->save()){throw new Exception('Resource save failed');}
  $modx->cacheManager->refresh();
  $t=$next;
 }catch(Throwable $e){
  $r->set('content',$beforeR);$r->set('template',$beforeTemplate);$r->save();
  $modx->cacheManager->refresh();
  http_response_code(500);echo json_encode(['error'=>'Save failed; previous resource restored']);exit;
 }
}
echo json_encode([
 'resource'=>$r->toArray(),'template'=>$t->toArray(),
 'template_users'=>$modx->getCount('modResource',['template'=>$t->get('id')]),
 'resource_sha'=>hash('sha256',$r->get('content')),
 'template_sha'=>hash('sha256',$t->get('content'))
],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
