<?php
header('Content-Type: application/json; charset=utf-8');header('Cache-Control: no-store');
if($_SERVER['REQUEST_METHOD']!=='POST'||!hash_equals('TOKEN_SHA',hash('sha256',$_SERVER['HTTP_X_NP_KEY']??''))){http_response_code(403);exit;}
define('MODX_API_MODE',true);require_once dirname(__DIR__,2).'/config.core.php';require_once MODX_CORE_PATH.'model/modx/modx.class.php';$modx=new modX();$modx->initialize('web');
function fail($m){http_response_code(409);echo json_encode(['error'=>$m]);exit;}
if($modx->getOption('site_url')!=='https://ne-prosto.ru/')fail('Wrong site');
$spec=json_decode(base64_decode('PAYLOAD_BASE64'),true);$p=$spec['payload'];$old=$spec['old'];$release=$spec['release'];$html=$spec['template'];$a=json_decode(file_get_contents('php://input'),true)['action']??'';
if(!in_array($a,['inspect','stage','publish','rollback'],true))fail('Invalid action');
$r=$modx->getObject('modResource',102);$t=$modx->getObject('modTemplate',['templatename'=>$release['template_name']]);
if(!$r||$r->get('uri')!==$p['uri']||(int)$r->get('parent')!==2||$r->get('deleted'))fail('Resource identity mismatch');
$current=hash('sha256',(string)$r->get('content'));
if(!in_array($current,[$release['expected_content_sha'],$release['target_content_sha']],true))fail('Article changed since review');
if(!in_array((int)$r->get('template'),[8,$t?(int)$t->get('id'):-1],true))fail('Unexpected article template');
if(hash('sha256',$p['content'])!==$release['target_content_sha']||hash('sha256',$html)!==$release['target_template_sha'])fail('Release integrity mismatch');
if($t&&hash('sha256',(string)$t->get('content'))!==$release['target_template_sha'])fail('Dedicated template changed');
foreach($p['tvs'] as $n=>$v)if((string)$r->getTVValue($n)!==(string)$v)fail('Article TV changed '.$n);
function state($r,$t,$modx){return ['resource'=>$r->toArray(),'template'=>$t?$t->toArray():null,'template_sha'=>$t?hash('sha256',(string)$t->get('content')):null,'source_template_sha'=>hash('sha256',(string)$modx->getObject('modTemplate',8)->get('content'))];}
if($a==='inspect'){echo json_encode(state($r,$t,$modx),JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);exit;}
$modx->beginTransaction();
try{
 if($a==='rollback'){$r->set('content',$old['content']);$r->set('template',8);if(!$r->save())throw new Exception('Restore failed');}
 else{
  if(!$t){$t=$modx->newObject('modTemplate');$t->set('templatename',$release['template_name']);$t->set('description','Isolated editorial layout for resource 102');$t->set('content',$html);if(!$t->save())throw new Exception('Template save failed');}
  foreach($modx->getCollection('modTemplateVarTemplate',['templateid'=>8]) as $binding){$key=['templateid'=>$t->get('id'),'tmplvarid'=>$binding->get('tmplvarid')];if(!$modx->getObject('modTemplateVarTemplate',$key)){$b=$modx->newObject('modTemplateVarTemplate');$b->fromArray($key);$b->set('rank',$binding->get('rank'));if(!$b->save())throw new Exception('TV binding save failed');}}
  $r->set('content',$p['content']);$r->set('template',$t->get('id'));if($a==='publish')$r->set('published',1);if(!$r->save())throw new Exception('Article save failed');
  $r=$modx->getObject('modResource',102);if(hash('sha256',(string)$r->get('content'))!==$release['target_content_sha']||(int)$r->get('template')!==(int)$t->get('id'))throw new Exception('Layout readback mismatch');
 }
 $modx->commit();$modx->cacheManager->refresh();if(function_exists('opcache_reset'))opcache_reset();echo json_encode(['ok'=>true,'id'=>102,'content_sha'=>hash('sha256',(string)$r->get('content')),'state'=>state($r,$t,$modx)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
}catch(Throwable $e){$modx->rollBack();fail($e->getMessage());}
