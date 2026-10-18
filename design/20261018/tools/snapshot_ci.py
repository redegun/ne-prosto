from pathlib import Path
import os,json,secrets,hashlib,ftplib,io,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parent
run=os.environ['GITHUB_RUN_ID']
backup=Path('/opt/office1080/ne-prosto-backups')/run;backup.mkdir(parents=True,exist_ok=True)
creds=json.loads(os.environ['NE_PROSTO_FTP'])
token=secrets.token_urlsafe(40);path='_agent_tmp/np-design-'+run+'/'+secrets.token_hex(12)+'.php'
source=(ROOT/'snapshot_bridge.php').read_text().replace('TOKEN_SHA',hashlib.sha256(token.encode()).hexdigest()).encode()
def connect():
 f=ftplib.FTP(creds['host'],timeout=90);f.login(creds['login'],creds['password']);return f
def mkdir(f,path):
 parts=path.split('/')
 for i in range(1,len(parts)+1):
  try:f.mkd('/'.join(parts[:i]))
  except ftplib.error_perm as e:
   if not str(e).startswith('550'):raise
with connect() as f:
 mkdir(f,str(Path('ne-prosto/public_html/'+path).parent))
 f.storbinary('STOR ne-prosto/public_html/'+path,io.BytesIO(source))
try:
 req=urllib.request.Request('https://ne-prosto.ru/'+path,data=b'{}',headers={'X-NP-Key':token,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=90) as response:data=response.read()
 snapshot=json.loads(data);assert snapshot['site_url']=='https://ne-prosto.ru/'
 (backup/'cms-snapshot.json').write_bytes(data)
 print('Snapshot saved:',backup, {k:len(snapshot[k]) for k in ['resources','templates','chunks']})
finally:
 with connect() as f:
  dest='ne-prosto/_agent_archives/np-design-'+run+'/'+Path(path).name;mkdir(f,str(Path(dest).parent));f.rename('ne-prosto/public_html/'+path,dest)
 try:
  with urllib.request.urlopen('https://ne-prosto.ru/'+path,timeout=30):raise AssertionError('Bridge is public')
 except urllib.error.HTTPError as e:assert e.code==404
 print('Bridge archived; public 404')
