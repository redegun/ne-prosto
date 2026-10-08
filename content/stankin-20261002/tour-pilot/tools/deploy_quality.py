from pathlib import Path
import ftplib,hashlib,json,sys
from deploy_tour import ROOT,REMOTE,ASSETS,connect
BACKUP=ROOT.parent/'sources/before-quality-20261008'
STATE=BACKUP/'upload-state.json'
def run():
 BACKUP.mkdir(parents=True,exist_ok=True)
 done=json.loads(STATE.read_text()) if STATE.exists() else {}
 with connect() as ftp:
  for name in ['index.html','tour.js','loader.js','tour.css']:
   backup=BACKUP/('live-'+name)
   if not backup.exists():
    with backup.open('wb') as out:ftp.retrbinary('RETR '+REMOTE+'/'+ASSETS+'/'+name,out.write)
  if sys.argv[-1]=='backup':
   print('Backed up live tour files',flush=True);return
  files=sorted(f for folder in ['details','vendor/environments','vendor/postprocessing','vendor/shaders','vendor/math'] for f in (ROOT/folder).rglob('*') if f.is_file())
  files += [ROOT/name for name in ['appearance.js','effects.js','detail-textures.js','tour.js','loader.js','index.html']]
  known=set()
  for index,src in enumerate(files):
   rel=src.relative_to(ROOT).as_posix();digest=hashlib.sha256(src.read_bytes()).hexdigest()
   if done.get(rel)==digest:continue
   dest=REMOTE+'/'+ASSETS+'/'+rel;parts=dest.split('/')[:-1]
   for n in range(1,len(parts)+1):
    directory='/'.join(parts[:n])
    if directory in known:continue
    try:ftp.mkd(directory)
    except ftplib.error_perm as exc:
     if not str(exc).startswith('550'):raise
    known.add(directory)
   staging=dest+'.upload'
   with src.open('rb') as data:ftp.storbinary('STOR '+staging,data,1024*1024)
   ftp.voidcmd('TYPE I')
   assert ftp.size(staging)==src.stat().st_size,rel
   ftp.rename(staging,dest)
   done[rel]=digest;STATE.write_text(json.dumps(done,indent=2))
   if index%40==0 or index>=len(files)-6:print(str(index+1)+'/'+str(len(files))+' '+rel,flush=True)
 print('Quality assets published; live entry point updated last',flush=True)
if __name__=='__main__':run()
