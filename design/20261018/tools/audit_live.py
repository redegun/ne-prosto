from pathlib import Path
from bs4 import BeautifulSoup as BS
import re,json,urllib.request,urllib.error,urllib.parse,concurrent.futures
R=Path(__file__).resolve().parent.parent
d=json.loads((R/'sources/cms-snapshot.json').read_text())
rs=[r for r in d['resources'] if r['published'] and not r['deleted'] and r['template'] in [1,4,5,6,7,8,9,10,11,12,13,14,15,16]]
before={e['path']:e for e in json.loads((R/'sources/page-index.json').read_text())}
def check(r):
 path='/' if r['id']==1 else '/'+r['uri'];url='https://ne-prosto.ru'+urllib.parse.quote(path,safe='/-_')
 try:
  with urllib.request.urlopen(url,timeout=90) as response:status=response.status;s=BS(response.read().decode(),'html.parser')
 except urllib.error.HTTPError as e:
  status=e.code;s=BS(e.read().decode(),'html.parser')
 title=s.title.get_text() if s.title else ''
 meta=s.select_one('meta[name=description]');desc=meta.get('content','') if meta else ''
 known=before.get(path,{})
 return {'id':r['id'],'path':path,'status':status,'template':r['template'],'h1':[x.get_text(' ',strip=True) for x in s.select('h1')],'header':len(s.select('.np-header')),'footer':len(s.select('.np-footer')),'title_unchanged':re.sub(r'[\x00-\x1f]','',known.get('title',title))==re.sub(r'[\x00-\x1f]','',title),'description_unchanged':known.get('description',desc)==desc,'raw_tags':'[[$' in s.get_text() or '[[!pdo' in s.get_text(),'projects':len(s.select('.np-project')),'articles':len(s.select('.np-article-card')),'placeholder':any(v in s.get_text() for v in ['тарам папмммим','А что здесь?','Red Hot Chili Peppers','радиолюбитель'])}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(check,rs))
(R/'sources/live-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
bad=[x for x in out if (x['status']!=200 and x['id']!=17) or len(x['h1'])!=1 or not x['header'] or not x['footer'] or not x['title_unchanged'] or not x['description_unchanged'] or x['raw_tags'] or x['placeholder']]
print('Pages',len(out),'issues',len(bad));print(json.dumps(bad,ensure_ascii=False,indent=2))
