import requests, json, sys, time
env={}
for l in open("/root/.openclaw/secrets.env",encoding="utf-8"):
    l=l.strip()
    if "=" in l and not l.startswith("#"):
        k,v=l.split("=",1); env[k.replace("export ","").strip()]=v.strip().strip('"').strip("'")
s=requests.Session(); s.headers["X-Keyso-TOKEN"]=env["KEYSSO_TOKEN"]
B="https://api.keys.so"
cmd=sys.argv[1]
if cmd=="create":
    typ=int(sys.argv[2]); name=sys.argv[3]; words=[w.strip() for w in open(sys.argv[4],encoding="utf-8") if w.strip()]
    data={"type":typ,"name":name,"regionId":225,"words":words}
    if typ==1: data.update(source=0, ws_types=[0,3,1])
    r=s.post(B+"/wordstat/create-project",json={"data":data},timeout=60); print(r.status_code,r.text[:500])
elif cmd=="status":
    r=s.get(B+"/wordstat/get-project-status",params={"id":sys.argv[2]},timeout=60); print(r.text[:300])
elif cmd=="report":
    out=[];p=1
    while True:
        r=s.get(B+"/wordstat/report",params={"projectId":sys.argv[2],"sort":"ws|desc","page":p,"per_page":500},timeout=90).json()
        out+=r.get("data",[])
        if p>=int(r.get("last_page",1)): break
        p+=1; time.sleep(1.1)
    json.dump(out,open(sys.argv[3],"w",encoding="utf-8"),ensure_ascii=False)
    print(len(out)); print(json.dumps(out[:2],ensure_ascii=False)[:800])
