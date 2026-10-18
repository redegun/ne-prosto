from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
from bs4 import BeautifulSoup as BS
import markdown
P=Path(__file__).resolve().parent
S=Path('/root/.openclaw/workspace/clients/peoplepay/content/articles/2026-10-18-pages-and-enquiries')
U='/blog/peoplepay-kakie-stranicy-prinosyat-obrashcheniya'
A='/images/godnota/peoplepay-pages-20261018/'
O=P/'preview';D=O/A.lstrip('/');D.mkdir(parents=True,exist_ok=True)
items=json.loads((S/'illustrations.json').read_text())
for item in items:
 src=S/item['file'];im=Image.open(src).convert('RGB');shutil.copy2(src,D/src.name)
 for w in sorted(set([min(im.width,640),min(im.width,1280),im.width])):
  im.resize((w,round(im.height*w/im.width)),Image.Resampling.LANCZOS).save(D/f'{src.stem}-{w}.webp',quality=94,method=6)
im=Image.new('RGB',(1600,900),'#f6f6f1');dr=ImageDraw.Draw(im)
def txt(x,y,text,size=40,strong=False,fill='#191b18'):
 font='/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if strong else '')+'.ttf'
 dr.text((x,y),text,font=ImageFont.truetype(font,size),fill=fill)
dr.rectangle((70,64,410,112),fill='#e9f77c');txt(90,72,'НЕПРОСТО / ПРАКТИКА',20,True)
txt(70,160,'Какие страницы',76,True);txt(70,252,'приводят к обращениям',76,True)
txt(75,372,'People Pay · 90 дней поискового трафика',31,False,'#666a62')
dr.line((75,458,1525,458),fill='#d8dbd2',width=2)
for x,label,v,g in [(75,'БЛОГ','39 554','83'),(875,'СТРАНЫ И КАРТЫ','4 211','77')]:
 txt(x,507,label,23,True,'#666a62');txt(x,562,v,78,True);txt(x,665,'поисковых визита' if x==75 else 'поисковых визитов',25,False,'#666a62');txt(x+400,562,g,78,True);txt(x+400,665,'целевых визита' if x==75 else 'целевых визитов',25,False,'#666a62')
txt(75,808,'Целевой визит — визит с автоцелью формы, не подтверждённая заявка CRM.',22,False,'#666a62')
im.save(D/'cover.webp',quality=94,method=6);im.resize((1200,675),Image.Resampling.LANCZOS).save(D/'cover-og.jpg',quality=92)
srcmd=(S/'article.md').read_text().split('\n',1)[1].lstrip()
content=BS(markdown.markdown(srcmd,extensions=['tables']),'html.parser');meta={Path(v['file']).name:v for v in items}
for tag in list(content.select('img')):
 src=S/tag['src'];item=meta[src.name]
 with Image.open(src) as pic:w,h=pic.size
 widths=sorted(set([min(w,640),min(w,1280),w]))
 tag.attrs.update({'src':A+f'{src.stem}-{min(w,1280)}.webp','srcset':', '.join(A+f'{src.stem}-{v}.webp {v}w' for v in widths),'sizes':'(max-width: 820px) 90vw, 780px','width':str(w),'height':str(h),'loading':'lazy','decoding':'async'})
 parent=tag.parent;fig=content.new_tag('figure',attrs={'class':'np-pp-figure'});link=content.new_tag('a',href=A+src.name,target='_blank',rel='noopener',attrs={'aria-label':'Открыть изображение в полном размере: '+tag.get('alt','')});tag.extract();link.append(tag);fig.append(link)
 caption=content.new_tag('figcaption');caption.string=item['caption'];fig.append(caption)
 nxt=parent.find_next_sibling()
 if nxt and nxt.name=='p' and nxt.find('em'):nxt.decompose()
 parent.replace_with(fig)
for table in list(content.select('table')):
 wrap=content.new_tag('div',attrs={'class':'np-pp-table','tabindex':'0','role':'region','aria-label':'Показатели страниц входа за 90 дней'});table.wrap(wrap)
 for th in table.select('thead th'):th['scope']='col'
wrapper=content.new_tag('div',attrs={'class':'np-pp-article'})
byline=content.new_tag('p',attrs={'class':'np-pp-byline'});byline.string='Антон Ветров · Разбор проекта People Pay · Данные за 20.07–17.10.2026';wrapper.append(byline)
for el in list(content.contents):wrapper.append(el.extract())
cta=content.new_tag('p',attrs={'class':'np-pp-cta'});cta.append('Хотите разобраться, какие страницы помогают получать обращения на вашем сайте? ');a=content.new_tag('a',href='/koordinatyi#request');a.string='Обсудим задачу';cta.append(a);wrapper.append(cta)
css='''.np-pp-article{min-width:0}.np-pp-article .np-pp-byline{font-size:14px;line-height:1.5;color:#666a62;margin-bottom:32px}.np-pp-article .np-pp-figure{margin:40px 0;max-width:100%}.np-pp-article .np-pp-figure>a{display:block}.np-pp-article .np-pp-figure img{display:block;width:100%;height:auto;margin:0;border:1px solid #d8dbd2}.np-pp-article .np-pp-figure figcaption{font-size:14px;line-height:1.5;color:#666a62;margin-top:12px}.np-pp-article .np-pp-table{overflow:auto;max-width:100%;margin:32px 0}.np-pp-article table{width:100%;border-collapse:collapse;min-width:650px;font-size:16px;line-height:1.45}.np-pp-article th,.np-pp-article td{padding:14px 12px;text-align:left;border-bottom:1px solid #d8dbd2}.np-pp-article th{vertical-align:bottom;background:#e9f77c}.np-pp-article td:not(:first-child){text-align:right;font-variant-numeric:tabular-nums}.np-pp-article .np-pp-cta{padding-top:28px;border-top:1px solid #d8dbd2}.np-pp-article a:focus-visible,.np-pp-article .np-pp-table:focus-visible{outline:3px solid #191b18;outline-offset:4px}@media(max-width:600px){.np-pp-article .np-pp-figure{margin:28px 0}.np-pp-article .np-pp-figure figcaption{font-size:13px}.np-pp-article .np-pp-byline{font-size:13px}}'''
(D/'article.css').write_text(css)
body=f'<link rel="stylesheet" href="{A}article.css?v=20261018-1">\n'+str(wrapper);(P/'content.html').write_text(body)
title='Какие страницы приводят к обращениям на сайте People Pay'
desc='Разбор People Pay за 90 дней: поисковый трафик, визиты с формой и вклад главной, блога, страниц карт и услуг. С цифрами и примерами доработок.'
payload={'pagetitle':title,'longtitle':title,'menutitle':'People Pay — трафик и обращения','alias':U.rsplit('/',1)[1],'parent':2,'template':8,'published':0,'deleted':0,'hidemenu':0,'isfolder':0,'searchable':1,'cacheable':1,'richtext':0,'context_key':'web','class_key':'modDocument','content_type':1,'uri_override':1,'uri':U.lstrip('/'),'introtext':'Блог даёт 84% поискового трафика. Страницы карт — почти столько же целевых визитов при значительно меньшей посещаемости. Разбираем данные и работы на People Pay.','description':desc,'content':body,'tvs':{'titl':'Какие страницы приводят к обращениям — People Pay | Непросто','desc':desc,'image':(A+'cover.webp').lstrip('/'),'page__image--big':'','author':'Антон Ветров','noindex':'','displayed_tag':''}}
(P/'payload.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
soup=BS((P/'source-page.html').read_text(),'html.parser')
if soup.base:soup.base.decompose()
soup.title.string=payload['tvs']['titl']
for script in list(soup.select('script')):script.decompose()
for field in ['.article-view','.article-publishing','.post__autor','.article-wrapper > .article__img']:
 for e in soup.select(field):e.decompose()
soup.h1.string=title
slot=soup.select_one('.article-content');slot.clear();slot.append(BS(body,'html.parser'))
for sel,val in [('meta[property="og:title"]',payload['tvs']['titl']),('meta[property="og:description"],meta[name="description"]',desc),('meta[property="og:url"]','https://ne-prosto.ru'+U),('meta[property="og:image"]','https://ne-prosto.ru'+A+'cover.webp')]:
 for tag in soup.select(sel):tag['content']=val
for m in soup.select('meta[name="robots"],link[rel="canonical"]'):m.decompose()
soup.head.append(soup.new_tag('meta',attrs={'name':'robots','content':'noindex,nofollow'}));soup.head.append(soup.new_tag('link',rel='canonical',href='https://ne-prosto.ru'+U))
crumb=soup.select_one('.breadcrumbs-item_active')
if crumb:crumb.string='People Pay — трафик и обращения'
for f in soup.select('form'):f['onsubmit']='event.preventDefault();return false'
for tag in soup.select('[src],link[href]'):
 for att in ['src','href']:
  if tag.has_attr(att) and tag[att].startswith('https://ne-prosto.ru/'):tag[att]=tag[att][len('https://ne-prosto.ru'):]
soup.body.append(soup.new_tag('script',defer='',src='/assets/neprosto/design-20261018/site.js?v=6'))
for a in soup.select('a[href]'):
 if a.get('href','').endswith('#np-main'):a['href']=U+'#np-main'
(O/'index.html').write_text(str(soup))
manifest=[{'local':str(f.relative_to(P)),'remote':A+f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(D.iterdir())]
(P/'assets-manifest.json').write_text(json.dumps(manifest,indent=2))
assert len(soup.select('h1'))==1
assert len(wrapper.select('figure'))==5
assert payload['published']==0
assert not any(v in body for v in ['D:/','ACCESS.md','232481135'])
print('Prepared',len(manifest),'assets;',sum(x['bytes'] for x in manifest),'bytes. Draft payload, 5 figures, one H1.')
