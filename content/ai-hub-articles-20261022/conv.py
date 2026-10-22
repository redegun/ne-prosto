import glob,os
from PIL import Image
D="/root/orch-tmp/task-503/img"
for f in glob.glob(D+"/*-orig.png"):
    n=os.path.basename(f)[:-9]
    if os.path.exists(f"{D}/{n}.jpg"): continue
    try: im=Image.open(f).convert("RGB")
    except Exception as e: print(n,"bad",e); continue
    w,h=im.size; th=round(w*2/3)
    if h!=th: top=max(0,(h-th)//2); im=im.crop((0,top,w,top+min(th,h)))
    im.resize((1536,1024),Image.LANCZOS).save(f"{D}/{n}.jpg",quality=85,optimize=True,progressive=True)
    im.resize((768,512),Image.LANCZOS).save(f"{D}/{n}-768.jpg",quality=82,optimize=True,progressive=True)
    print(n,"ok",w,h)
