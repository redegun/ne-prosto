"""Crop original-resolution atlas details; no full giant texture is sent to the GPU."""
from pathlib import Path
from PIL import Image,ImageStat
import json,sys,gc
Image.MAX_IMAGE_PIXELS=None
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
names={1:'Вагон_1_внутри.jpg',2:'Вагон_2_внутри.jpg',3:'Вагон_3_внутри.jpg',4:'Вагон_4_внутри.jpg',5:'Внутри_5_2.jpg',6:'Вагон_6_внутри_Света.jpg',7:'Вагон_7_внутри.jpg',8:'Внутри_вагон_8.jpg'}
for car,name in names.items():
    out=root/'web'/'details'/f'car-{car}';out.mkdir(parents=True,exist_ok=True)
    records={}
    with Image.open(root/'textures-interior'/name) as original:
        original.load();w,h=original.size
        for row in range(8):
            for col in range(8):
                x0=round(col*w/8);x1=round((col+1)*w/8);y0=round(row*h/8);y1=round((row+1)*h/8)
                box=(max(0,x0-4),max(0,y0-4),min(w,x1+4),min(h,y1+4))
                tile=original.crop(box).convert('RGB')
                thumb=tile.copy();thumb.thumbnail((64,64));stat=ImageStat.Stat(thumb);thumb.close()
                if min(stat.mean)>254 and max(stat.stddev)<1:
                    tile.close();continue
                key=f'{col}-{row}'
                tile.save(out/f'{key}.jpg',quality=95,optimize=True,subsampling=0)
                tile.thumbnail((1600,1600),Image.Resampling.LANCZOS)
                tile.save(out/f'{key}-mobile.jpg',quality=93,optimize=True,subsampling=0)
                records[key]={'rect':[box[0]/w,box[1]/h,w/(box[2]-box[0]),h/(box[3]-box[1])]}
                tile.close()
    (out/'manifest.json').write_text(json.dumps({'grid':8,'width':w,'height':h,'tiles':records}),encoding='utf-8')
    gc.collect();print('DETAIL_TILES',car,len(records),flush=True)
