"""Produce UV-addressed exterior texture assets, preserving the supplied artwork."""
from pathlib import Path
from PIL import Image,ImageStat
import json,sys,gc,hashlib
Image.MAX_IMAGE_PIXELS=None
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
base=root/'web'/'exterior';base.mkdir(exist_ok=True)
records=[]
for car in range(1,9):
    source=root/'textures-exterior'/f'{car}_Вагон.jpg'
    out=root/'web'/'exterior-details'/f'car-{car}';out.mkdir(parents=True,exist_ok=True)
    tiles={}
    with Image.open(source) as im:
        im.load();w,h=im.size
        preview=im.crop((0,0,w,round(h*.425)))
        preview=preview.resize((4096,1741),Image.Resampling.LANCZOS)
        preview.save(base/f'car-{car}.jpg',quality=94,optimize=True,subsampling=0);preview.close()
        for row in range(4):
            for col in range(8):
                x0=round(col*w/8);x1=round((col+1)*w/8);y0=round(row*h/8);y1=round((row+1)*h/8)
                box=(max(0,x0-4),max(0,y0-4),min(w,x1+4),min(h,y1+4))
                tile=im.crop(box).convert('RGB');thumb=tile.copy();thumb.thumbnail((64,64));stat=ImageStat.Stat(thumb);thumb.close()
                if min(stat.mean)>254 and max(stat.stddev)<1:tile.close();continue
                key=f'{col}-{row}'
                tile.save(out/f'{key}.jpg',quality=94,optimize=True,subsampling=0)
                tile.thumbnail((1600,1600),Image.Resampling.LANCZOS)
                tile.save(out/f'{key}-mobile.jpg',quality=92,optimize=True,subsampling=0);tile.close()
                tiles[key]={'rect':[box[0]/w,box[1]/h,w/(box[2]-box[0]),h/(box[3]-box[1])]}
    (out/'manifest.json').write_text(json.dumps({'grid':8,'width':w,'height':h,'tiles':tiles}),encoding='utf-8')
    records.append({'car':car,'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'base_bytes':(base/f'car-{car}.jpg').stat().st_size,'detail_tiles':len(tiles)})
    print('EXTERIOR_READY',car,len(tiles),flush=True);gc.collect()
(base/'manifest.json').write_text(json.dumps({'source':'https://disk.yandex.ru/d/T2sgQL_nKO3pYA','uv_split':.425,'cars':records},ensure_ascii=False,indent=2),encoding='utf-8')
