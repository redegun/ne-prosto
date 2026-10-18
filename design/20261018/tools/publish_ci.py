from pathlib import Path
import os,json,secrets,hashlib,ftplib,io,urllib.request,urllib.error,concurrent.futures
ROOT=Path(__file__).resolve().parent.parent
run=os.environ['GITHUB_RUN_ID'];backup=Path('/opt/office1080/ne-prosto-backups')/run;backup.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'cms-manifest.json').read_text());changes=manifest['changes']
sha=lambda b:hashlib.sha256(b).hexdigest()
for c in changes:
 b=(ROOT/c['path']).read_bytes();assert sha(b)==c['target'];c['content']=b.decode()
creds=json.loads(os.environ['NE_PROSTO_FTP']);token=secrets.token_urlsafe(40)
path='_agent_tmp/np-publish-'+run+'/'+secrets.token_hex(12)+'.php'
source=(ROOT/'tools/publish_bridge.php').read_text().replace('TOKEN_SHA',sha(token.encode())).encode()
def connect():
 f=ftplib.FTP(creds['host'],timeout=90);f.login(creds['login'],creds['password']);return f
def mkdir(f,path):
 parts=path.split('/')
 for i in range(1,len(parts)+1):
  try:f.mkd('/'.join(parts[:i]))
  except ftplib.error_perm as e:
   if not str(e).startswith('550'):raise
def request(action):
 body=json.dumps({'action':action,'changes':changes},ensure_ascii=False).encode()
 req=urllib.request.Request('https://ne-prosto.ru/'+path,data=body,headers={'X-NP-Key':token,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=120) as r:return r.read()
 except urllib.error.HTTPError as e:
  print('Bridge error:',e.code,e.read().decode()[:400]);raise
with connect() as f:
 mkdir(f,str(Path('ne-prosto/public_html/'+path).parent));f.storbinary('STOR ne-prosto/public_html/'+path,io.BytesIO(source))
try:
 before=request('inspect');state=json.loads(before);assert state['site_url']==manifest['site']
 (backup/'cms-before.json').write_bytes(before)
 (backup/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 assets={}
 with connect() as f:
  assetdir='ne-prosto/public_html/assets/neprosto/design-20261018';mkdir(f,assetdir)
  for name in ['site.css','site.js']:
   b=(ROOT/'assets'/name).read_bytes();target=assetdir+'/'+name;old=io.BytesIO()
   try:f.retrbinary('RETR '+target,old.write)
   except ftplib.error_perm as e:
    if not str(e).startswith('550'):raise
   if old.getvalue():(backup/('old-'+name)).write_bytes(old.getvalue())
   temp=target+'.'+run+'.tmp';f.storbinary('STOR '+temp,io.BytesIO(b));f.rename(temp,target)
   check=io.BytesIO();f.retrbinary('RETR '+target,check.write);assert sha(check.getvalue())==sha(b)
   assets[name]=sha(b)
 result=request('apply');answer=json.loads(result);assert answer['ok']
 assert [x['hash'] for x in answer['readback']]==[x['target'] for x in changes]
 (backup/'cms-after.json').write_bytes(result);(backup/'assets.json').write_text(json.dumps(assets))
 print('Applied:',answer['updated'],'objects; verified:',len(changes),'assets:',assets,'backup:',backup)
finally:
 with connect() as f:
  dest='ne-prosto/_agent_archives/np-publish-'+run+'/'+Path(path).name;mkdir(f,str(Path(dest).parent));f.rename('ne-prosto/public_html/'+path,dest)
 try:
  with urllib.request.urlopen('https://ne-prosto.ru/'+path,timeout=30):raise AssertionError('Bridge is public')
 except urllib.error.HTTPError as e:assert e.code==404
 print('Bridge archived; public 404')
paths=['/','/portfolio/','/uslugi/','/uslugi/sajtyi','/uslugi/logotipyi-firmennyie-stili','/kompaniya/','/kompaniya/klientyi/','/kompaniya/v-rolyax/','/kompaniya/vakansii/','/koordinatyi','/blog/','/blog/gde-brat-foto-i-illyustracii-stoki','/portfolio/firmaflis','/portfolio/logotip-dlya-geodezicheskojkompanii-arshin','/portfolio/presentation-anglomania','/portfolio/poezd-stankin','/portfolio/lrrazbor-poisk']
def verify(path):
 with urllib.request.urlopen('https://ne-prosto.ru'+path,timeout=90) as r:b=r.read().decode();assert r.status==200
 assert 'np-site' in b and 'np-header' in b and 'np-footer' in b,path
 assert '[[!pdoResources' not in b and '[[$np_' not in b,path
 (backup/('page-'+str(paths.index(path))+'.html')).write_text(b)
 return path
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for p in pool.map(verify,paths):print('HTTP and shell OK',p)
for name,h in assets.items():
 with urllib.request.urlopen('https://ne-prosto.ru/assets/neprosto/design-20261018/'+name+'?run='+run,timeout=30) as r:assert sha(r.read())==h
print('Public assets match source')
