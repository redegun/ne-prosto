from pathlib import Path
import os,sys,json,hashlib,secrets,base64,ftplib,io,urllib.request,urllib.error,re,time
P=Path(__file__).resolve().parent;W='https://ne-prosto.ru/';R='ne-prosto/public_html';sha=lambda b:hashlib.sha256(b).hexdigest()
def validate():
 p=json.loads((P/'payload.json').read_text());m=json.loads((P/'assets-manifest.json').read_text());rel=json.loads((P/'release.json').read_text())
 assert p['uri']=='blog/kakie-stranicy-pomogayut-poluchat-obrashcheniya' and len(m)==3
 assert sha(p['content'].encode())==rel['target_content_sha']
 for x in m:
  b=(P/x['local']).read_bytes();assert sha(b)==x['sha256'] and len(b)==x['bytes'];assert x['remote'].startswith('/images/godnota/stranicy-i-obrashcheniya/')
 for text in [p['content'],p['pagetitle'],p['introtext'],p['description'],str(p['tvs']),(P/'template.html').read_text()]:assert not any(x in text.lower() for x in ['2026','90 дней','39 554','4 211','46 925','47 925','1901','428','315','июля','октября','нячанг','nha-trang','232481135'])
 return p,m,rel
def main():
 p,m,rel=validate()
 if '--check' in sys.argv:print('Validated named case, percentage charts, protected details and three public assets');return
 run=os.environ['GITHUB_RUN_ID'];b=Path('/opt/office1080/ne-prosto-backups')/run;b.mkdir(parents=True,exist_ok=True);c=json.loads(os.environ['NE_PROSTO_FTP']);key=secrets.token_urlsafe(40);path='_agent_tmp/editorial-privacy-'+run+'/'+secrets.token_hex(12)+'.php'
 spec={'payload':p,'release':rel,'template':(P/'template.html').read_text()};source=(P/'bridge.php').read_text().replace('TOKEN_SHA',sha(key.encode())).replace('SPEC_BASE64',base64.b64encode(json.dumps(spec,ensure_ascii=False).encode()).decode()).encode()
 def ftp():
  f=ftplib.FTP(c['host'],timeout=90);f.login(c['login'],c['password']);return f
 def mkdir(f,d):
  ps=d.split('/')
  for i in range(1,len(ps)+1):
   try:f.mkd('/'.join(ps[:i]))
   except ftplib.error_perm as e:
    if not str(e).startswith('550'):raise
 def call(a):
  q=urllib.request.Request(W+path,data=json.dumps({'action':a}).encode(),headers={'X-NP-Key':key,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(q,timeout=90) as r:return json.load(r)
  except urllib.error.HTTPError as e:
   try:msg=json.loads(e.read()).get('error','Bridge error')
   except Exception:msg='Bridge response invalid'
   raise RuntimeError('Bridge HTTP '+str(e.code)+': '+msg) from None
 def get(u):
  for i in range(3):
   try:
    with urllib.request.urlopen(u,timeout=60) as r:return r.read()
   except urllib.error.HTTPError as e:
    if e.code not in (502,503,504) or i==2:raise
    time.sleep(2)
 with ftp() as f:mkdir(f,str(Path(R+'/'+path).parent));f.storbinary('STOR '+R+'/'+path,io.BytesIO(source))
 try:
  before=call('inspect');(b/'cms-before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2));call('hide');print('Saved backup and hid article for privacy update',flush=True)
  archive='ne-prosto/_agent_archives/editorial-privacy-'+run
  retired=[]
  with ftp() as f:
   # Exact client-specific directories only; all contents remain recoverable outside webroot.
   for src,name in [(R+'/images/godnota/peoplepay-pages-20261018','original-assets'),(R+'/assets/cache_image/images/godnota/peoplepay-pages-20261018','cached-thumbnails')]:
    try:f.cwd('/');f.cwd(src);exists=True
    except ftplib.error_perm:exists=False
    f.cwd('/')
    if exists:mkdir(f,archive);f.rename(src,archive+'/'+name);retired.append(src)
   (b/'retired-paths.json').write_text(json.dumps(retired,indent=2))
   for x in m:
    target=R+x['remote'];mkdir(f,str(Path(target).parent));old=io.BytesIO();exists=False
    try:f.retrbinary('RETR '+target,old.write);exists=True
    except ftplib.error_perm as e:
     if not str(e).startswith('550'):raise
    if exists:assert sha(old.getvalue())==x['sha256'],'Unexpected existing public asset'
    else:
     temp=target+'.upload-'+run;f.storbinary('STOR '+temp,io.BytesIO((P/x['local']).read_bytes()));z=io.BytesIO();f.retrbinary('RETR '+temp,z.write);assert sha(z.getvalue())==x['sha256'];f.rename(temp,target)
  for x in m:assert sha(get(W.rstrip('/')+x['remote']+'?run='+run))==x['sha256']
  after=call('apply');assert after['ok'];(b/'cms-after.json').write_text(json.dumps(after,ensure_ascii=False,indent=2))
  for u in [p['uri'],'blog/','']:
   text=get(W+u).decode()
   assert rel['old_uri'] not in text and '/images/godnota/peoplepay-pages-20261018/' not in text
   if u==p['uri']:
    assert not any(x in text.lower() for x in ['39 554','4 211','46 925','20.07','17.10','232481135'])
    assert 'People Pay' in text and 'pp-data-chart' in text and 'pp-rate-chart' in text
    assert text.lower().count('<h1')==1 and 'pp-neutral-flow' in text
  retired_urls=[W+rel['old_uri']]+[W.rstrip('/')+x for x in json.loads((P/'retire-caches.json').read_text())]
  old=json.loads((P.parent/'peoplepay-pages-20261018/assets-manifest.json').read_text())
  retired_urls += [W.rstrip('/')+x['remote'] for x in old]
  for u in retired_urls:
   try:get(u);raise AssertionError('Retired sensitive URL still responds: '+u)
   except urllib.error.HTTPError as e:assert e.code in [403,404,410],e.code
  out={'ok':True,'resource':102,'url':W+p['uri'],'run':run,'retired_urls_verified':len(retired_urls),'archive':archive,'backup':str(b)};(b/'publication.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
 finally:
  with ftp() as f:
   dest='ne-prosto/_agent_archives/editorial-privacy-'+run+'/'+Path(path).name;mkdir(f,str(Path(dest).parent));f.rename(R+'/'+path,dest)
  try:get(W+path);raise AssertionError('Bridge is public')
  except urllib.error.HTTPError as e:assert e.code==404
  print('Bridge archived; public URL 404',flush=True)
if __name__=='__main__':main()
