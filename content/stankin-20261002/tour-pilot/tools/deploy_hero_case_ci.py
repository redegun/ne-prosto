"""Publish the reviewed full-width case opening; no changes to the 3D renderer."""
from pathlib import Path
import base64,io,os,json,hashlib,secrets,ftplib,urllib.request,urllib.error,sys
ROOT=Path(__file__).resolve().parent.parent.parent
REMOTE='ne-prosto/public_html'
WEB='https://ne-prosto.ru/'
ALLOWED={'hero.css','hero-train-960.webp','hero-train-1920.webp'}
def digest(data):return hashlib.sha256(data).hexdigest()
def validate():
 m=json.loads((ROOT/'release-hero-20261018.json').read_text())
 assert m['resource']==100 and m['template']==15
 for key,name in [('resource','content.html'),('template','template.html')]:
  assert digest((ROOT/name).read_bytes())==m[key+'_sha']['target']
 assert {x['name'] for x in m['files']}==ALLOWED
 for row in m['files']:
  data=(ROOT/'assets'/row['name']).read_bytes()
  assert digest(data)==row['sha256'] and len(data)==row['bytes']
 return m
def main():
 m=validate()
 if '--check' in sys.argv:print('Validated hero assets, resource 100 and dedicated template 15');return
 credentials=json.loads(os.environ['NE_PROSTO_FTP']);run=os.environ['GITHUB_RUN_ID']
 backup=Path('/opt/office1080/ne-prosto-backups')/run;backup.mkdir(parents=True,exist_ok=True)
 def connect():
  f=ftplib.FTP(credentials['host'],timeout=90);f.login(credentials['login'],credentials['password']);return f
 def mkdir(f,path):
  parts=path.split('/')
  for i in range(1,len(parts)+1):
   try:f.mkd('/'.join(parts[:i]))
   except ftplib.error_perm as e:
    if not str(e).startswith('550'):raise
 token=secrets.token_urlsafe(40)
 path='_agent_tmp/stankin-hero-'+run+'/'+secrets.token_hex(12)+'.php'
 spec={}
 for key,name in [('resource','content.html'),('template','template.html')]:
  spec[key]={**m[key+'_sha'],'content':(ROOT/name).read_text()}
 source=(ROOT/'tour-pilot/tools/deploy_hero_case.php').read_text().replace('TOKEN_SHA',digest(token.encode())).replace('SPEC_BASE64',base64.b64encode(json.dumps(spec,ensure_ascii=False).encode()).decode()).encode()
 def call(action):
  req=urllib.request.Request(WEB+path,data=json.dumps({'action':action}).encode(),headers={'Content-Type':'application/json','X-Stankin-Key':token})
  with urllib.request.urlopen(req,timeout=90) as resp:return json.load(resp)
 with connect() as f:
  mkdir(f,str(Path(REMOTE+'/'+path).parent));f.storbinary('STOR '+REMOTE+'/'+path,io.BytesIO(source))
 try:
  before=call('read')
  print('Current resource template:',before['resource']['template'],'uses:',before['template_users'],flush=True)
  (backup/'cms-before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2))
  for key in ['resource','template']:
   assert before[key+'_sha'] in [m[key+'_sha']['expected'],m[key+'_sha']['target']],key+' changed since preparation'
  with connect() as f:
   for row in m['files']:
    remote=REMOTE+'/images/portfolio/stankin/'+row['name']
    previous=io.BytesIO()
    try:f.retrbinary('RETR '+remote,previous.write)
    except ftplib.error_perm as e:
     if not str(e).startswith('550'):raise
    else:
     data=previous.getvalue();(backup/row['name']).write_bytes(data)
     assert digest(data)==row['sha256'],'Unexpected existing asset '+row['name']
    temporary=remote+'.upload-'+run
    with (ROOT/'assets'/row['name']).open('rb') as stream:f.storbinary('STOR '+temporary,stream)
    f.voidcmd('TYPE I');assert f.size(temporary)==row['bytes']
    f.rename(temporary,remote)
    print('Published '+row['name'],flush=True)
  for row in m['files']:
   with urllib.request.urlopen(WEB+'images/portfolio/stankin/'+row['name']+'?release='+run,timeout=40) as resp:data=resp.read()
   assert digest(data)==row['sha256'],'Asset HTTP hash mismatch'
  after=call('publish')
  for key in ['resource','template']:
   assert after[key+'_sha']==m[key+'_sha']['target'],key+' readback mismatch'
  (backup/'cms-after.json').write_text(json.dumps(after,ensure_ascii=False,indent=2))
  with urllib.request.urlopen(WEB+'portfolio/poezd-stankin',timeout=60) as resp:html=resp.read().decode()
  assert 'hero.css?v=20261018-hero1' in html and html.count('<h1')==1 and len(html.encode())>30000
  assert html.index('st-case__hero') < html.index('id="tour"') < html.index('st-case__brief')
  assert 'process-title__text' not in html and '20261018-screen1' in html
  (backup/'case-after.html').write_text(html)
  print('Dedicated template:',after['resource']['template'],flush=True)
  print('Case and template published and HTTP verified; backup:',backup,flush=True)
 finally:
  with connect() as f:
   archive='ne-prosto/_agent_archives/stankin-hero-'+run+'/'+Path(path).name
   mkdir(f,str(Path(archive).parent));f.rename(REMOTE+'/'+path,archive)
  try:
   with urllib.request.urlopen(WEB+path,timeout=30):raise AssertionError('Bridge still public')
  except urllib.error.HTTPError as e:assert e.code==404
  print('Temporary bridge archived; public URL 404',flush=True)
if __name__=='__main__':main()
