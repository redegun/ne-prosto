from pathlib import Path
import re,ftplib,json,secrets,hashlib,urllib.request,sys,subprocess
ROOT=Path(__file__).resolve().parent.parent
STATE=ROOT.parent/'endpoint-tour-state.json'
SOURCE=Path('/root/.openclaw/workspace/clients/antonvetrov/ACCESS.md')
REMOTE='ne-prosto/public_html'
ASSETS='images/portfolio/stankin/tour-20261008'
WEB='https://ne-prosto.ru/'
BACKUP=ROOT.parent/'sources/before-tour-20261008'
def connect():
 s=SOURCE.read_text().split('## FTP',1)[1].split('## ',1)[0]
 d={k:v.strip().strip(chr(96)) for k,v in re.findall(r'\*\*([^:]+):\*\*\s*([^\n]+)',s)}
 ftp=ftplib.FTP(d['Хост'],timeout=90);ftp.login(d['Логин'],d['Пароль']);return ftp
def dirs(ftp,path):
 parts=path.split('/')
 for i in range(1,len(parts)+1):
  try:ftp.mkd('/'.join(parts[:i]))
  except ftplib.error_perm as e:
   if not str(e).startswith('550'):raise
def store(ftp,src,dest):
 dirs(ftp,str(Path(dest).parent).replace(chr(92),'/'))
 with src.open('rb') as f:ftp.storbinary('STOR '+dest,f,1024*1024)
 ftp.voidcmd('TYPE I');assert ftp.size(dest)==src.stat().st_size,dest
def call(action,**values):
 st=json.loads(STATE.read_text())
 req=urllib.request.Request(WEB+st['path'],data=json.dumps({'action':action,**values}).encode(),headers={'Content-Type':'application/json','X-Stankin-Key':st['token']})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
cmd=sys.argv[1]
if cmd=='assets':
 files=[ROOT/n for n in ['index.html','tour.css','tour.js','loader.js','embed.js','embed.css']]
 files+=list((ROOT/'models').glob('*.glb'))+list((ROOT/'vendor').rglob('*'))
 with connect() as ftp:
  for src in files:
   if src.is_file():store(ftp,src,REMOTE+'/'+ASSETS+'/'+src.relative_to(ROOT).as_posix())
 print('Uploaded tour assets',len([f for f in files if f.is_file()]))
elif cmd=='prepare':
 BACKUP.mkdir(parents=True,exist_ok=True)
 assert not STATE.exists(),'Existing endpoint state: inspect before continuing'
 token=secrets.token_urlsafe(40);path='_agent_tmp/stankin-tour-20261008/'+secrets.token_hex(12)+'.php'
 endpoint="""<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD']!=='POST' || !hash_equals('TOKEN_SHA', hash('sha256', $_SERVER['HTTP_X_STANKIN_KEY'] ?? ''))) {http_response_code(403);exit;}
define('MODX_API_MODE', true);
require_once dirname(__DIR__, 2).'/config.core.php';
require_once MODX_CORE_PATH.'model/modx/modx.class.php';
$modx=new modX();$modx->initialize('web');
$r=$modx->getObject('modResource',100);
if(!$r){http_response_code(404);exit;}
$in=json_decode(file_get_contents('php://input'),true);
$before=$r->get('content');
if(($in['action']??'')==='update'){
 if(!hash_equals(hash('sha256',$before),$in['expected']??'')){http_response_code(409);echo json_encode(['error'=>'Content changed']);exit;}
 $next=$in['content']??'';
 if(strlen($next)<strlen($before) || strpos($next,'data-stankin-tour')===false){http_response_code(422);exit;}
 $r->set('content',$next);
 if(!$r->save()){http_response_code(500);exit;}
 $modx->cacheManager->refresh();
}
echo json_encode(['resource'=>$r->toArray(),'sha256'=>hash('sha256',$r->get('content'))],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
""".replace('TOKEN_SHA',hashlib.sha256(token.encode()).hexdigest())
 f=BACKUP/'endpoint.php';f.write_text(endpoint);subprocess.run(['docker','run','--rm','-i','--network','none','--entrypoint','php','rybkavprud-feed-dev:php74','-l'],input=endpoint.encode(),check=True)
 STATE.write_text(json.dumps({'path':path,'token':token}));STATE.chmod(0o600)
 with connect() as ftp:store(ftp,f,REMOTE+'/'+path)
 before=call('read');(BACKUP/'resource.json').write_text(json.dumps(before,ensure_ascii=False,indent=2))
 old=before['resource']['content']
 assert old==(ROOT.parent/'content.html').read_text(),'Live content differs from repository; inspect backup'
 marker='<section class="st-case__section"><div class="st-case__copy"><p class="st-case__eyebrow">03 / Визуализации</p>'
 assert old.count(marker)==1
 section="""<section class="st-case__section" id="tour"><div class="st-case__copy"><p class="st-case__eyebrow">Интерактивная 3D-модель</p><h2>Пройдите по вагонам</h2><p>Мы перенесли рабочую модель в браузер, чтобы вы могли рассмотреть оформление в объёме. Выберите один из восьми вагонов, пройдите по салону и поверните обзор к интересной детали. Для знакомства с интерьером есть маршрут из пяти точек.</p></div><a class="st-tour-launch" data-stankin-tour href="/ASSETS/"><img src="/images/portfolio/stankin/render-interior-2-10.jpg" alt="Рабочая визуализация салона поезда СТАНКИН" width="1920" height="1080" loading="lazy" decoding="async"><span>Начать 3D-экскурсию →</span></a><p class="st-tour-note">Интерактивная версия нашей рабочей 3D-модели. На компьютере — мышь и клавиши WASD, на телефоне — касания и стрелки на экране. <a href="/ASSETS/" target="_blank" rel="noopener">Открыть экскурсию отдельно →</a></p></section>""".replace('ASSETS',ASSETS)
 new='<link rel="stylesheet" href="/'+ASSETS+'/embed.css">'+old.replace(marker,section+marker)+'<script defer src="/'+ASSETS+'/embed.js"></script>'
 (BACKUP/'content.html').write_text(old);(ROOT.parent/'content-with-tour.html').write_text(new)
 print('Prepared live backup and new case; current SHA',before['sha256'])
elif cmd=='publish':
 before=json.loads((BACKUP/'resource.json').read_text())
 new=(ROOT.parent/'content-with-tour.html').read_text()
 result=call('update',expected=before['sha256'],content=new)
 assert result['sha256']==hashlib.sha256(new.encode()).hexdigest()
 (ROOT.parent/'tour-published.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 (ROOT.parent/'content.html').write_text(new)
 # Warm the case after cache clearing, before any parallel checks.
 with urllib.request.urlopen(WEB+'portfolio/poezd-stankin',timeout=45) as r:html=r.read().decode()
 assert 'data-stankin-tour' in html and len(html)>10000
 print('Published and warmed case 100',result['sha256'])
elif cmd=='cleanup':
 st=json.loads(STATE.read_text());source=REMOTE+'/'+st['path']
 target='ne-prosto/_agent_archives/stankin-tour-20261008/'+Path(st['path']).name
 with connect() as ftp:
  dirs(ftp,str(Path(target).parent));ftp.rename(source,target)
 try:
  with urllib.request.urlopen(WEB+st['path'],timeout=30) as r:raise AssertionError('Endpoint still public: '+str(r.status))
 except urllib.error.HTTPError as e:assert e.code==404,e.code
 (ROOT.parent/'tour-endpoint-cleanup.json').write_text(json.dumps({'status':404,'archived_outside_webroot':True}))
 print('Endpoint archived; public URL 404')
