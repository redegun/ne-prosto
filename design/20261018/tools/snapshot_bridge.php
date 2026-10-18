<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if($_SERVER['REQUEST_METHOD']!=='POST'||!hash_equals('TOKEN_SHA',hash('sha256',$_SERVER['HTTP_X_NP_KEY']??''))){http_response_code(403);exit;}
define('MODX_API_MODE',true);
require_once dirname(__DIR__,2).'/config.core.php';
require_once MODX_CORE_PATH.'model/modx/modx.class.php';
$modx=new modX();$modx->initialize('web');
if(strpos($modx->getOption('site_url'),'ne-prosto.ru')===false){http_response_code(409);exit;}
$out=['site_url'=>$modx->getOption('site_url'),'created_at'=>gmdate('c')];
foreach(['resources'=>'modResource','templates'=>'modTemplate','chunks'=>'modChunk','tvs'=>'modTemplateVar','tv_bindings'=>'modTemplateVarTemplate','tv_values'=>'modTemplateVarResource'] as $key=>$class){
 $out[$key]=[];
 foreach($modx->getCollection($class) as $object){$out[$key][]=$object->toArray();}
}
$out['snippet_names']=[];
foreach($modx->getCollection('modSnippet') as $object){$out['snippet_names'][]=['id'=>$object->get('id'),'name'=>$object->get('name')];}
echo json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
