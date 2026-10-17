"""Publish only the checked STANKIN panoramic view release from the office CI runner."""
from pathlib import Path
import os,json,hashlib,ftplib,sys,urllib.request
ROOT=Path(__file__).resolve().parent.parent
REMOTE='ne-prosto/public_html/images/portfolio/stankin/tour-20261008'
WEB='https://ne-prosto.ru/images/portfolio/stankin/tour-20261008/'
ENTRY=['detail-textures.js','appearance.js','effects.js','station.js','train-overview.js','tour.css','tour.js','loader.js','index.html','embed.css','embed.js']
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate():
 manifest=json.loads((ROOT/'release-wide-20261018.json').read_text())
 for row in manifest['files']:
  rel=Path(row['path']);path=(ROOT/rel).resolve()
  assert path.is_relative_to(ROOT.resolve()) and path.is_file()
  assert rel.as_posix() in ENTRY or rel.parts[0] in ['overview']
  assert digest(path)==row['sha256'] and path.stat().st_size==row['bytes'],str(rel)
 return manifest
def main():
 manifest=validate()
 if '--check' in sys.argv:print('Validated',len(manifest['files']),'release files');return
 credentials=json.loads(os.environ['NE_PROSTO_FTP'])
 backup=Path('/opt/office1080/ne-prosto-backups')/os.environ['GITHUB_RUN_ID'];backup.mkdir(parents=True,exist_ok=True)
 statefile=backup/'uploaded.json';done=json.loads(statefile.read_text()) if statefile.exists() else {}
 ftp=ftplib.FTP(credentials['host'],timeout=90);ftp.login(credentials['login'],credentials['password'])
 try:
  for name,expected in manifest['expected_live'].items():
   target=backup/name
   if not target.exists():
    with target.open('wb') as stream:ftp.retrbinary('RETR '+REMOTE+'/'+name,stream.write)
   assert digest(target)==expected,'Live file changed since preparation: '+name
  dirs=set()
  for index,row in enumerate(manifest['files']):
   rel=row['path']
   if done.get(rel)==row['sha256']:continue
   for length in range(1,len((REMOTE+'/'+rel).split('/'))):
    directory='/'.join((REMOTE+'/'+rel).split('/')[:length])
    if directory in dirs:continue
    try:ftp.mkd(directory)
    except ftplib.error_perm as exc:
     if not str(exc).startswith('550'):raise
    dirs.add(directory)
   destination=REMOTE+'/'+rel;temporary=destination+'.upload-'+os.environ['GITHUB_RUN_ID']
   with (ROOT/rel).open('rb') as stream:ftp.storbinary('STOR '+temporary,stream,1024*1024)
   ftp.voidcmd('TYPE I');assert ftp.size(temporary)==row['bytes'],rel
   ftp.rename(temporary,destination)
   done[rel]=row['sha256'];statefile.write_text(json.dumps(done))
   if index%40==0 or rel in ENTRY:print(str(index+1)+'/'+str(len(manifest['files']))+' '+rel,flush=True)
 finally:
  try:ftp.quit()
  except OSError:ftp.close()
 for row in manifest['files']:

  with urllib.request.urlopen(WEB+row['path']+'?release=20261018-'+os.environ['GITHUB_RUN_ID'],timeout=40) as response:data=response.read()
  assert hashlib.sha256(data).hexdigest()==row['sha256'],'HTTP mismatch: '+row['path']
 print('Published and verified; backup:',backup,flush=True)
if __name__=='__main__':main()
