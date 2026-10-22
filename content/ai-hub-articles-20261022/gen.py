import json,os,sys,base64,io,requests,concurrent.futures as cf
from PIL import Image
D="/root/orch-tmp/task-503"; os.makedirs(D+"/img",exist_ok=True)
key=os.environ["POLZA_API_KEY"]; style=open(D+"/style.txt").read().strip()
P=json.load(open(D+"/prompts.json"))
def one(name):
    out=f"{D}/img/{name}.jpg"
    if os.path.exists(out): return name,"exists"
    for attempt in range(2):
        try:
            r=requests.post("https://polza.ai/api/v1/images/generations",headers={"Authorization":"Bearer "+key},
              json={"model":"openai/gpt-image-2.5-flare","prompt":style+"\n"+P[name],"size":"1536x1024","n":1},timeout=300)
            j=r.json()
            if r.status_code>=300: err=str(j)[:300]; continue
            d=j["data"][0]
            b=base64.b64decode(d["b64_json"]) if d.get("b64_json") else requests.get(d["url"],timeout=120).content
            im=Image.open(io.BytesIO(b)).convert("RGB")
            im.save(f"{D}/img/{name}-orig.png")
            im.resize((1200,800),Image.LANCZOS).save(out,quality=86,optimize=True,progressive=True)
            im.resize((768,512),Image.LANCZOS).save(f"{D}/img/{name}-768.jpg",quality=84,optimize=True,progressive=True)
            return name,"ok %dx%d"%im.size
        except Exception as e: err=repr(e)[:300]
    return name,"ERR "+err
with cf.ThreadPoolExecutor(8) as ex:
    for n,s in ex.map(one,list(P)): print(n,s,flush=True)
