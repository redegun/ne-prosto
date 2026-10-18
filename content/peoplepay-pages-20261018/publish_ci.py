from pathlib import Path
import os,sys,json,hashlib,secrets,base64,ftplib,io,urllib.request,urllib.error,time,re
P=Path(__file__).resolve().parent
WEB='https://ne-prosto.ru/';REMOTE='ne-prosto/public_html'
sha=lambda b:hashlib.sha256(b).hexdigest()
def validate():
 p=json.loads((P/'payload.json').read_text());m=json.loads((P/'assets-manifest.json').read_text())
 assert p['parent']==2 and p['template']==8 and p['published']==0
 assert p['uri']=='blog/peoplepay-kakie-stranicy-prinosyat-obrashcheniya'
 assert p['content']==(P/'content.html').read_text()
 assert len(m)==25 and len({a['remote'] for a in m})==len(m)
 for a in m:
  assert a['remote'].startswith('/images/godnota/peoplepay-pages-20261018/')
  b=(P/a['local']).read_bytes();assert len(b)==a['bytes'] and sha(b)==a['sha256']
 return p,m
def main():
 payload,assets=validate()
 if '--check' in sys.argv:print('Validated article payload and all 25 whitelisted assets');return
 run=os.environ['GITHUB_RUN_ID'];backup=Path('/opt/office1080/ne-prosto-backups')/run;backup.mkdir(parents=True,exist_ok=True)
 creds=json.loads(os.environ['NE_PROSTO_FTP']);token=secrets.token_urlsafe(40);path='_agent_tmp/peoplepay-'+run+'/'+secrets.token_hex(12)+'.php'
 spec={'payload':payload,'old':json.loads((P/'payload-v1.json').read_text()),'release':json.loads((P/'release-v2.json').read_text()),'template':(P/'template-v2.html').read_text()}
 source=(P/'publish_bridge_v2.php').read_text().replace('TOKEN_SHA',sha(token.encode())).replace('PAYLOAD_BASE64',base64.b64encode(json.dumps(spec,ensure_ascii=False).encode()).decode()).encode()
 def ftp():
  f=ftplib.FTP(creds['host'],timeout=90);f.login(creds['login'],creds['password']);return f
 def mkdir(f,d):
  parts=d.split('/')
  for i in range(1,len(parts)+1):
   try:f.mkd('/'.join(parts[:i]))
   except ftplib.error_perm as e:
    if not str(e).startswith('550'):raise
 def call(action):
  req=urllib.request.Request(WEB+path,data=json.dumps({'action':action}).encode(),headers={'Content-Type':'application/json','X-NP-Key':token})
  try:
   with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)
  except urllib.error.HTTPError as e:
   try:message=json.loads(e.read()).get('error','Bridge error')
   except Exception:message='Non-JSON bridge response'
   raise RuntimeError('Bridge HTTP '+str(e.code)+': '+message) from None
 def fetch(url):
  for n in range(3):
   try:
    with urllib.request.urlopen(url,timeout=60) as r:return r.read()
   except urllib.error.HTTPError as e:
    if e.code not in [502,503,504] or n==2:raise
    time.sleep(2*(n+1))
 with ftp() as f:
  mkdir(f,str(Path(REMOTE+'/'+path).parent));f.storbinary('STOR '+REMOTE+'/'+path,io.BytesIO(source))
 published=False
 try:
  before=call('inspect');(backup/'cms-before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2));(backup/'assets-manifest.json').write_text(json.dumps(assets))
  print('Backed up CMS state; existing resource:',before['resource']['id'] if before['resource'] else None,flush=True)
  inventory=[]
  with ftp() as f:
   for a in assets:
    target=REMOTE+a['remote'];mkdir(f,str(Path(target).parent));old=io.BytesIO();exists=False
    try:f.retrbinary('RETR '+target,old.write);exists=True
    except ftplib.error_perm as e:
     if not str(e).startswith('550'):raise
    if exists:assert sha(old.getvalue())==a['sha256'],'Unexpected existing asset '+a['remote']
    inventory.append({'path':target,'existed':exists,'sha256':sha(old.getvalue()) if exists else None})
    (backup/'asset-before.json').write_text(json.dumps(inventory,indent=2))
    if not exists:
     tmp=target+'.upload-'+run;f.storbinary('STOR '+tmp,io.BytesIO((P/a['local']).read_bytes()));check=io.BytesIO();f.retrbinary('RETR '+tmp,check.write);assert sha(check.getvalue())==a['sha256'];f.rename(tmp,target)
  for a in assets:assert sha(fetch(WEB.rstrip('/')+a['remote']+'?release='+run))==a['sha256']
  print('All 25 assets match public HTTP SHA256',flush=True)
  stage=call('stage');published=True;assert stage['ok'] and stage['content_sha']==sha(payload['content'].encode());(backup/'cms-staged.json').write_text(json.dumps(stage,ensure_ascii=False,indent=2))
  result=call('publish');published=True;assert result['ok'] and result['state']['resource']['published'];assert result['state']['template_sha']==spec['release']['target_template_sha'];assert result['state']['source_template_sha']==before['source_template_sha']
  (backup/'cms-after.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
  # Sequential warmup after clearing MODX cache.
  pages={}
  for u in [payload['uri'],'blog/','']:
   b=fetch(WEB+u).decode();pages[u]=b
   if u==payload['uri']:
    assert len(re.findall(r'<h1\b',b,re.I))==1 and 'pp-reading-grid' in b
    assert len(re.findall(r'<figure\b[^>]*class="np-pp-figure(?: [^"]*)?"',b))==5
    assert payload['tvs']['titl'] in b and '[[*' not in b and '[[!pdoResources' not in b
    assert 'noindex' not in ''.join(re.findall(r'<meta[^>]*name="robots"[^>]*>',b,re.I))
   elif u=='blog/':assert payload['alias'] in b,'Article absent from blog list'
  (backup/'article-after.html').write_text(pages[payload['uri']])
  summary={'ok':True,'run':run,'resource':result['id'],'url':WEB+payload['uri'],'content_sha':result['content_sha'],'assets_verified':len(assets),'template':result['state']['resource']['template'],'source_template_unchanged':True,'backup':str(backup)}
  (backup/'publication.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
 except Exception:
  if published:
   try:call('rollback');print('Previous article layout restored after failed verification',flush=True)
   except Exception:print('ROLLBACK NEEDS ATTENTION',flush=True)
  raise
 finally:
  with ftp() as f:
   dest='ne-prosto/_agent_archives/peoplepay-'+run+'/'+Path(path).name;mkdir(f,str(Path(dest).parent));f.rename(REMOTE+'/'+path,dest)
  try:fetch(WEB+path);raise AssertionError('Bridge still public')
  except urllib.error.HTTPError as e:assert e.code==404
  print('Bridge archived, public endpoint 404',flush=True)
if __name__=='__main__':main()
