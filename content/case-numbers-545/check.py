import re, html, urllib.request, sys
B="https://ne-prosto.ru"; PV=B+"/_preview/draft-b05c9e2f0a8cddea/"
urls={1:B+"/blog/kuda-propadayut-zayavki-iz-messendzherov",2:PV+"skorost-otveta-na-zayavku.html",3:PV+"zapisi-zvonkov-dlya-ii-assistenta.html",4:PV+"chto-sprosit-u-klienta-pri-pervom-obrashhenii.html",5:PV+"kak-poschitat-poteryannye-zayavki.html"}
txt=open("inserts.txt",encoding="utf-8").read()
blocks=re.split(r"\n(?=\d\. «)",txt)
def norm(s): s=html.unescape(re.sub(r"<[^>]+>"," ",s)); s=s.replace(" "," ").replace("‑","-"); return re.sub(r"\s+"," ",s)
ok=True
for b in blocks:
    n=int(b[0]); paras=[p.strip() for p in b.split("\n") if p.strip() and not p.startswith("Место:") and not re.match(r"\d\. «",p)]
    req=urllib.request.Request(urls[n]+"?nocache=546",headers={"User-Agent":"Mozilla/5.0 task546"})
    r=urllib.request.urlopen(req); h=r.read().decode(); t=norm(h)
    for p in paras:
        c=t.count(norm(p)); print(n,r.status,"OK" if c==1 else f"FAIL x{c}",p[:50]); ok&=c==1
    print(n,"h1",h.count("<h1"),"cta",h.count('<aside class="np-cta '),"footer","footer" in h)
print("ALL OK" if ok else "FAILED")
