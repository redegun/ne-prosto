"""Build compact browser atlases from the supplied original interior and exterior artwork."""
from pathlib import Path
from PIL import Image
import sys
Image.MAX_IMAGE_PIXELS=None
root=Path(sys.argv[1])
out=root/'textures-overview';out.mkdir(exist_ok=True)
names={1:'Вагон_1_внутри.jpg',2:'Вагон_2_внутри.jpg',3:'Вагон_3_внутри.jpg',4:'Вагон_4_внутри.jpg',5:'Внутри_5_2.jpg',6:'Вагон_6_внутри_Света.jpg',7:'Вагон_7_внутри.jpg',8:'Внутри_вагон_8.jpg'}
size=1536;split=round(size*.425)
for car,name in names.items():
 with Image.open(root/'textures-browser'/name) as im:base=im.convert('RGB').resize((size,size),Image.Resampling.LANCZOS)
 with Image.open(root/'textures-exterior'/f'{car}_Вагон.jpg') as im:
  top=im.crop((0,0,im.width,round(im.height*.425))).resize((size,split),Image.Resampling.LANCZOS)
 base.paste(top,(0,0));base.save(out/f'car-{car}.jpg',quality=91,subsampling=0)
 print('Prepared overview atlas',car,flush=True)
