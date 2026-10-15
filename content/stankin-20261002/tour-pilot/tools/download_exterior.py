"""Fetch supplied exterior atlases with SHA validation; prepare inspection thumbnails."""
import pathlib,json,urllib.request,urllib.parse,hashlib,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
Image.MAX_IMAGE_PIXELS=None
root=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path(__file__).parent
root.mkdir(parents=True,exist_ok=True)
dest=root/'textures-exterior';dest.mkdir(exist_ok=True)
key='https://disk.yandex.ru/d/T2sgQL_nKO3pYA'
api='https://cloud-api.yandex.net/v1/disk/public/resources'
def metadata(path=None):
    params={'public_key':key,'limit':100}
    if path:params['path']=path
    with urllib.request.urlopen(api+'?'+urllib.parse.urlencode(params),timeout=40) as response:return json.load(response)
results=[]
for item in metadata()['_embedded']['items']:
    assert item['type']=='file' and item['mime_type']=='image/jpeg',item['name']
    out=dest/pathlib.Path(item['name']).name
    for attempt in range(3):
        item=metadata(item['path'])
        if not(out.exists() and out.stat().st_size==item['size'] and hashlib.sha256(out.read_bytes()).hexdigest()==item['sha256']):
            url=api+'/download?'+urllib.parse.urlencode({'public_key':key,'path':item['path']})
            with urllib.request.urlopen(url,timeout=40) as r:download=json.load(r)['href']
            digest=hashlib.sha256();partial=out.with_suffix('.part')
            with urllib.request.urlopen(download,timeout=90) as response,partial.open('wb') as stream:
                while chunk:=response.read(1024*1024):digest.update(chunk);stream.write(chunk)
            if digest.hexdigest()!=item['sha256']:continue
            partial.replace(out)
        if metadata(item['path'])['sha256']!=item['sha256']:continue
        with Image.open(out) as im:
            dimensions=im.size;im.draft('RGB',(1600,1600));im.thumbnail((1600,1600))
            im.convert('RGB').save(dest/(out.stem+'-preview.jpg'),quality=90)
        row={'name':out.name,'bytes':item['size'],'sha256':item['sha256'],'dimensions':dimensions}
        results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True);break
    else:raise RuntimeError('Source changed during download: '+out.name)
(dest/'manifest.json').write_text(json.dumps({'source':key,'images':results},ensure_ascii=False,indent=2),encoding='utf-8')
