<?php
header('Content-Type: application/json; charset=utf-8');header('Cache-Control: no-store');
if($_SERVER['REQUEST_METHOD']!=='POST'||!hash_equals('TOKEN_SHA',hash('sha256',$_SERVER['HTTP_X_NP_KEY']??''))){http_response_code(403);exit;}
define('MODX_API_MODE',true);require_once dirname(__DIR__,2).'/config.core.php';require_once MODX_CORE_PATH.'model/modx/modx.class.php';$modx=new modX();$modx->initialize('web');
function fail($m){http_response_code(409);echo json_encode(['error'=>$m]);exit;}
if($modx->getOption('site_url')!=='https://ne-prosto.ru/')fail('Wrong site');
$s=json_decode(base64_decode('SPEC_BASE64'),true);$p=$s['payload'];$release=$s['release'];$html=$s['template'];$a=json_decode(file_get_contents('php://input'),true)['action']??'';
if(!in_array($a,['inspect','hide','apply'],true))fail('Invalid action');
$r=$modx->getObject('modResource',102);$t=$modx->getObject('modTemplate',18);
if(!$r||!$t||(int)$r->get('parent')!==2||(int)$r->get('template')!==18||$r->get('deleted'))fail('Resource identity mismatch');
if((int)$modx->getCount('modResource',['template'=>18])!==1)fail('Template is shared');
if(!in_array($r->get('uri'),[$release['old_uri'],$p['uri']],true))fail('URI changed');
if(!in_array(hash('sha256',(string)$r->get('content')),[$release['expected_content_sha'],$release['target_content_sha']],true))fail('Article changed');
if(!in_array(hash('sha256',(string)$t->get('content')),[$release['expected_template_sha'],$release['target_template_sha']],true))fail('Template changed');
$collision=$modx->getObject('modResource',['uri'=>$p['uri']]);if($collision&&(int)$collision->get('id')!==102)fail('New URI occupied');
function state($r,$t){$tv=[];foreach(['titl','desc','image','author','page__image--big','noindex','displayed_tag'] as $n)$tv[$n]=$r->getTVValue($n);return ['resource'=>$r->toArray(),'template'=>$t->toArray(),'tvs'=>$tv];}
if($a==='inspect'){echo json_encode(state($r,$t),JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);exit;}
$modx->beginTransaction();
try{
 if($a==='hide'){$r->set('published',0);if(!$r->save())throw new Exception('Hide failed');}
 else{
  if(hash('sha256',$p['content'])!==$release['target_content_sha']||hash('sha256',$html)!==$release['target_template_sha'])throw new Exception('Release mismatch');
  $t->set('content',$html);$t->set('templatename','Editorial article pages and enquiries');if(!$t->save())throw new Exception('Template save failed');
  foreach(['pagetitle','longtitle','menutitle','alias','uri','introtext','description','content'] as $n)$r->set($n,$p[$n]);$r->set('uri_override',1);$r->set('published',1);if(!$r->save())throw new Exception('Article save failed');
  foreach($p['tvs'] as $n=>$v)if(!$r->setTVValue($n,$v))throw new Exception('TV save failed');
  $r=$modx->getObject('modResource',102);if(hash('sha256',(string)$r->get('content'))!==$release['target_content_sha']||$r->get('uri')!==$p['uri'])throw new Exception('Readback mismatch');
  foreach($p['tvs'] as $n=>$v)if((string)$r->getTVValue($n)!==(string)$v)throw new Exception('TV readback mismatch');
 }
 $modx->commit();$modx->cacheManager->refresh();if(function_exists('opcache_reset'))opcache_reset();echo json_encode(['ok'=>true,'state'=>state($r,$t)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
}catch(Throwable $e){$modx->rollBack();fail($e->getMessage());}
