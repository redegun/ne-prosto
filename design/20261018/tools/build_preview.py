from pathlib import Path
from bs4 import BeautifulSoup as BS
import json,re,html
from urllib.parse import urljoin
R=Path('/root/.openclaw/workspace/sites/ne-prosto/design/20261018');O=R/'preview';O.mkdir(exist_ok=True)
d=json.loads((R/'sources/cms-snapshot.json').read_text());rs={x['id']:x for x in d['resources']}
tv={(x['contentid'],x['tmplvarid']):x['value'] for x in d['tv_values']}
chunks={p.stem:p.read_text() for p in (R/'chunks').glob('*.html')}
oldhome=BS((R/'sources/pages/9.html').read_text(),'html.parser')
email=oldhome.select_one('a[href^="mailto:"]')['href'][7:]
phone=oldhome.select_one('.contacts-phone').get_text(' ',strip=True)
def basic(s,res):
 s=s.replace('[[*longtitle:empty=`[[*pagetitle]]`]]',html.escape(res['longtitle'] or res['pagetitle']))
 for k in ['pagetitle','introtext','content','alias','id']:s=s.replace('[[*'+k+']]',str(res[k]))
 s=s.replace('[[~[[*id]]]]','/'+res['uri'])
 s=s.replace('[[++e-mail]]',email).replace('[[++phone:replace=` ==`:replace=`-==`]]',re.sub(r'[^+\d]','',phone)).replace('[[++phone]]',phone).replace('[[yearsActive]]','2026')
 for _ in range(3):s=re.sub(r'\[\[\$([\w_]+)\]\]',lambda m:chunks.get(m[1],''),s)
 return s.replace('[[++e-mail]]',email).replace('[[++phone:replace=` ==`:replace=`-==`]]',re.sub(r'[^+\\d]','',phone)).replace('[[++phone]]',phone).replace('[[yearsActive]]','2026').replace('[[~[[*id]]]]','/'+res['uri'])
def cards(parent,limit=100,exclude=[]):
 selected=sorted([x for x in rs.values() if x['parent']==parent and x['published'] and not x['deleted'] and x['id'] not in exclude],key=lambda x:x['menuindex'])[:limit]
 out=''
 for x in selected:
  image=tv.get((x['id'],5),''); title=html.escape(x['pagetitle']);intro=BS(x['introtext'],'html.parser').get_text()
  if parent==23:out+=f'<article class="np-project"><a class="np-project__image" href="/{x["uri"]}"><img src="/{image}" alt="{title}" width="1200" height="900" loading="lazy"><span class="np-project__arrow">↗</span></a><div class="np-project__caption"><h2><a href="/{x["uri"]}">{title}</a></h2><p>{intro}</p></div></article>'
  else:out+=f'<article class="np-article-card"><a class="np-article-card__image" href="/{x["uri"]}"><img src="/{image}" alt="" loading="lazy"></a><div><p class="np-kicker">Дизайн и практика</p><h2><a href="/{x["uri"]}">{title}</a></h2><p>{intro}</p></div></article>'
 return out
form=chunks['request_form']
form=form[:form.index('[[!AjaxForm?')]+form[form.index('<form '):form.index('</form>')+7]+'</div></div>'
chunks['request_form']=form
routes={}
for entry in json.loads((R/'sources/page-index.json').read_text()):
 if entry.get('status')!=200:continue
 path=entry['path'];res=next((x for x in rs.values() if '/'+x['uri']==path),None)
 if path=='/':res=rs[1]
 if not res:continue
 s=BS((R/'sources'/entry['file']).read_text(),'html.parser')
 tid=res['template']
 if tid in [1,5,9,13]:
  body=(R/f'templates/{tid}.html').read_text().split('<body',1)[1]
  body='<body'+body.split('</html>')[0]
  body=basic(body,res)
  def pdo(m):
   v=m[0];parent=int(re.search(r'&parents=`(\d+)`',v)[1]);lm=re.search(r'&limit=`(\d+)`',v);limit=int(lm[1]) if lm and int(lm[1]) else 100
   return cards(parent,limit,[100] if '&resources=`-100`' in v else [])
  body=re.sub(r'\[\[!pdoResources\?[\s\S]*?\]\]',pdo,body)
  # Filters in static preview use existing rendered controls.
  body=re.sub(r'<div class="np-filters[\s\S]*?</div>',lambda m:'<div class="np-filters np-wrap">'+''.join(str(x) for x in s.select('a.category-item'))+'</div>',body)
  body=re.sub(r'\[\[[\s\S]*?\]\]','',body)
  s.body.replace_with(BS(body,'html.parser').body)
 else:
  s.body['class']=s.body.get('class',[])+['np-site',f'np-template-{tid}']
  for sel,name in [('.header, .page__header','np_header'),('.footer, .page__footer','np_footer')]:
   el=s.select_one(sel)
   if el:el.replace_with(BS(basic(chunks[name],res),'html.parser'))
  oldform=s.select_one('.request')
  if oldform:oldform.replace_with(BS(basic(form,res),'html.parser'))
  heading=s.select_one('.title-main, .process-title__text')
  if heading and not s.h1:heading.name='h1'
  if res['id'] in [19,20,22,11,12,13]:
   target=s.select_one('.article-content')
   target.clear();target.append(BS((R/f'resources/{res["id"]}.html').read_text(),'html.parser'))
   s.body['class']+=['np-service-detail']
  if tid==4:
   el=s.select_one('.page__content');el.name='main';el['id']='np-main'
 s.head.insert(0,BS('<meta charset="utf-8">','html.parser'))
 for script in s.select('script'):script.decompose()
 if s.base:s.base.decompose()
 for el in s.select('[src],link[href],source[srcset],[style]'):
  for att in ['src','href']:
   if el.has_attr(att):el[att]=urljoin('https://ne-prosto.ru/',el[att])
  if el.has_attr('srcset'):el['srcset']=re.sub(r'(^|, )/',r'\1https://ne-prosto.ru/',el['srcset'])
  if el.has_attr('style'):el['style']=re.sub(r'url\((assets/[^)]+)\)',r'url(https://ne-prosto.ru/\1)',el['style'])
 for el in s.select('form'):el['onsubmit']='event.preventDefault()'
 s.head.append(BS('<link rel="stylesheet" href="/_design/site.css"><script defer src="/_design/site.js"></script>','html.parser'))
 filename=f'{res["id"]}.html';(O/filename).write_text(str(s));routes[path]=filename
(O/'routes.json').write_text(json.dumps(routes))
print('Preview pages',len(routes))
