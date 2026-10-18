"""Version only two embed links in MODX resource 100, via an ephemeral guarded bridge."""
from pathlib import Path
import io,os,json,hashlib,secrets,ftplib,urllib.request,urllib.error,sys
ROOT=Path(__file__).resolve().parent.parent
REMOTE='ne-prosto/public_html'
WEB='https://ne-prosto.ru/'
def digest(data):return hashlib.sha256(data).hexdigest()
def validate():
 m=json.loads((ROOT/'release-texture-case-20261018.json').read_text())
 assert m['resource']==100 and digest((ROOT.parent/'content.html').read_bytes())==m['target']
 assert (ROOT/'tools/version_embed_texture.php').is_file()
 return m
def main():
 m=validate()
 if '--check' in sys.argv:print('Validated exact resource 100 embed version change');return
 credentials=json.loads(os.environ['NE_PROSTO_FTP'])
 run=os.environ['GITHUB_RUN_ID'];backup=Path('/opt/office1080/ne-prosto-backups')/run;backup.mkdir(parents=True,exist_ok=True)
 token=secrets.token_urlsafe(40);path='_agent_tmp/stankin-texture-'+run+'/'+secrets.token_hex(12)+'.php'
 source=(ROOT/'tools/version_embed_texture.php').read_text().replace('TOKEN_SHA',digest(token.encode())).replace('EXPECTED_SHA',m['expected']).replace('TARGET_SHA',m['target']).encode()
 def connect():
  ftp=ftplib.FTP(credentials['host'],timeout=60);ftp.login(credentials['login'],credentials['password']);return ftp
 def mkdir(ftp,path):
  parts=path.split('/')
  for i in range(1,len(parts)+1):
   try:ftp.mkd('/'.join(parts[:i]))
   except ftplib.error_perm as e:
    if not str(e).startswith('550'):raise
 def call(action):
  req=urllib.request.Request(WEB+path,data=json.dumps({'action':action}).encode(),headers={'Content-Type':'application/json','X-Stankin-Key':token})
  with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)
 with connect() as ftp:
  mkdir(ftp,str(Path(REMOTE+'/'+path).parent));ftp.storbinary('STOR '+REMOTE+'/'+path,io.BytesIO(source))
 try:
  before=call('read');(backup/'resource-100-before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2))
  assert before['sha256'] in [m['expected'],m['target']],'Resource changed since preparation'
  after=call('version')
  assert after['sha256']==m['target'],'Resource readback mismatch'
  (backup/'resource-100-after.json').write_text(json.dumps(after,ensure_ascii=False,indent=2))
  with urllib.request.urlopen(WEB+'portfolio/poezd-stankin',timeout=60) as response:html=response.read().decode()
  assert 'embed.css?v=20261018-texture1' in html and 'embed.js?v=20261018-texture1' in html and len(html)>10000
  print('Resource 100 versioned and warmed; backup:',backup,flush=True)
 finally:
  with connect() as ftp:
   archive='ne-prosto/_agent_archives/stankin-texture-'+run+'/'+Path(path).name
   mkdir(ftp,str(Path(archive).parent));ftp.rename(REMOTE+'/'+path,archive)
  try:
   with urllib.request.urlopen(WEB+path,timeout=30) as response:raise AssertionError('Bridge still public')
  except urllib.error.HTTPError as error:assert error.code==404
  print('Temporary bridge archived outside webroot; public URL 404',flush=True)
if __name__=='__main__':main()
