#!/usr/bin/env bash
# Публикатор статей блога ne-prosto.ru /blog/ для автопилота office-seo-ne-prosto-blog (#862).
# usage: publish.sh <meta.json> [--dry-run]
#   meta.json: {"alias","pagetitle","introtext","description","titl","contentFile","cover",
#               "images":[{"file","name"}], "cta":{"title","text","button","place"}}
#   Пути — относительно workspace VPS (или абсолютные).
#   cover (jpg/png, ширина ≥1200) -> public_html/images/godnota/blog/<alias>.jpg (1536 по ширине) + <alias>-768.jpg,
#     TV image + page__image--big (карточка блога, обложка под H1, og:image) — как у статей хаба #503.
#   images -> images/godnota/blog/<alias>/<name>.jpg; в content ссылаться /images/godnota/blog/<alias>/<name>.jpg
# Ресурс создаёт хостинговый скрипт ~/ne-prosto/_autopilot/np-publish.php (MODX API, parent 2, template 8,
# published=1) по SSH-ключу ~/.ssh/ne-prosto_publish (Timeweb не поддерживает command= в authorized_keys).
# Коды выхода: 0 ok, 3 дубль (alias уже есть в MODX или живой URL 200), 2 ошибка входа, 1 сбой.
set -Eeuo pipefail
WS=/root/.openclaw/workspace
meta=${1:?usage: publish.sh <meta.json> [--dry-run]}
dry=0; [[ ${2:-} == --dry-run ]] && dry=1
cd "$WS"
abs() { [[ $1 == /* ]] && printf '%s' "$1" || printf '%s/%s' "$WS" "$1"; }
die() { echo "PUBLISH_ERROR: $*" >&2; exit "${2:-1}"; }
meta=$(abs "$meta"); [[ -f $meta ]] || die "no meta $meta" 2
alias=$(jq -r '.alias // empty' "$meta")
[[ $alias =~ ^[a-z0-9-]{3,90}$ ]] || die "bad alias '$alias'" 2
url="https://ne-prosto.ru/blog/$alias"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$url" || true)
if [[ $code == 200 ]]; then echo "{\"success\":false,\"error\":\"exists\",\"url\":\"$url\"}"; exit 3; fi
payload=$(mktemp); trap 'rm -f "$payload"' EXIT
python3 - "$meta" "$WS" "$payload" <<'PY' || die "build payload" 2
import base64, io, json, re, sys
from PIL import Image
meta_path, ws, out = sys.argv[1:4]
m = json.load(open(meta_path, encoding="utf-8"))
p = lambda x: x if x.startswith("/") else f"{ws}/{x}"
def need(k):
    v = (m.get(k) or "").strip()
    if not v: sys.exit(f"meta needs {k}")
    return v
alias = need("alias")
content = open(p(need("contentFile")), encoding="utf-8").read()
if re.search(r"<h1", content, re.I): sys.exit("content contains <h1> (template prints H1)")
if f"images/godnota/blog/{alias}.jpg" in content: sys.exit("cover duplicated inside content")
def jpg(path, width):
    im = Image.open(path).convert("RGB")
    if im.width < 1200: sys.exit(f"image too small {im.size} {path}")
    if im.width != width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=85, optimize=True, progressive=True)
    return base64.b64encode(b.getvalue()).decode()
cover = p(need("cover"))
imgs = []
for it in m.get("images") or []:
    name = it["name"]
    if not re.fullmatch(r"[a-z0-9-]{2,60}", name): sys.exit(f"bad image name {name}")
    if f"/images/godnota/blog/{alias}/{name}.jpg" not in content: print(f"WARN: image {name} not referenced in content", file=sys.stderr)
    imgs.append({"name": name, "b64": jpg(p(it["file"]), 1200)})
for src in re.findall(r'<img[^>]+src="([^"]+)"', content):
    if src.startswith(f"/images/godnota/blog/{alias}/") and not any(src.endswith(f"/{i['name']}.jpg") for i in imgs):
        sys.exit(f"content references missing image {src}")
d = {k: need(k) for k in ("pagetitle", "introtext", "description", "titl")}
if not (len(d["titl"]) <= 75): sys.exit("titl > 75")
d.update(alias=alias, content=content, cover_b64=jpg(cover, 1536), cover768_b64=jpg(cover, 768),
         images=imgs, cta=m.get("cta") or {})
json.dump(d, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(f"payload ok chars={len(re.sub('<[^>]+>', '', content))} images={len(imgs)}", file=sys.stderr)
PY
SSHH=(ssh -o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=20 -i /root/.ssh/ne-prosto_publish redegun@vh306.timeweb.ru)
mode=publish; (( dry )) && mode=dry
set +e
resp=$(timeout 300 "${SSHH[@]}" "/opt/php83/bin/php /home/r/redegun/ne-prosto/_autopilot/np-publish.php $mode" < "$payload")
rc=$?
set -e
echo "$resp"
exit $rc
