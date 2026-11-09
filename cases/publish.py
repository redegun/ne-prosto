#!/usr/bin/env python3
"""Мини-кейсы «Что сделали» для ne-prosto.ru (#1882).

cases/<client>.yml  →  хостинг ~/ne-prosto/np-cases/<slug портфолио>.json (вне webroot)
                     +  public_html/assets/neprosto/cases/<slug>/<картинки> и cases.css
Сниппет MODX npCases читает json: [[!npCases]] в content кейса, карточка — чанк np_project.

  python3 publish.py                 # проверка всех yml (lint), ничего не выкладывает
  python3 publish.py merci kppf --apply
  python3 publish.py --all --apply   # все yml с publish: true, только изменившиеся
Лёгкий (PyYAML + Pillow), можно с VPS и с ПК. Ключ: VPS /root/.ssh/ne-prosto_publish, на ПК — свой ssh-ключ.
"""
import argparse, hashlib, io, json, os, re, shutil, subprocess, sys, tarfile, tempfile
import yaml
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = "redegun@vh306.timeweb.ru"
KEY = "/root/.ssh/ne-prosto_publish"
HOME = "/home/r/redegun/ne-prosto"
ASSETS = "public_html/assets/neprosto/cases"
CSS_V = 2
TYPES = {"сайт", "дизайн", "SEO", "контент", "боты", "аналитика", "автоматизация", "видео"}
STATE = os.path.join(HERE, ".published.json")

# абсолютные цифры клиента и ПДн (правило sites/ne-prosto/memory/stageshow.md)
BAD = [
    (re.compile(r"\d[\d\s.,]*\s*(₽|руб|р\.|тыс|млн|\$|€)", re.I), "деньги"),
    (re.compile(r"(?<![×x+−-])\b\d[\d\s]{2,}\s*(визит|заяв|лид|звон|клиент|посетит|продаж|заказ)", re.I), "абсолютная цифра"),
    (re.compile(r"\+?\d[\d\s()-]{9,}\d"), "телефон"),
    (re.compile(r"[\w.+-]+@[\w-]+\.\w+"), "e-mail"),
    (re.compile(r"\b(CVE|IP|ssh|ftp|пароль|токен|#\d{2,})\b", re.I), "техническое"),
    (re.compile(r"\b(Саня|Сократ|Codex|Claude|OpenClaw)\b"), "внутренние имена"),
]
PUBLIC = ("title", "task", "done", "result")


def lint(d, path):
    errs = []
    for k in ("client", "name", "cases"):
        if not d.get(k) and k != "cases":
            errs.append(f"{path}: нет поля {k}")
    if d.get("publish") and not d.get("portfolio"):
        errs.append(f"{path}: publish без portfolio")
    texts = []
    if d.get("metric"):
        texts.append(("metric", f'{d["metric"].get("value", "")} {d["metric"].get("label", "")}'))
    for c in d.get("cases") or []:
        if c.get("type") not in TYPES:
            errs.append(f'{path}: {c.get("id")}: тип «{c.get("type")}» не из списка')
        for k in PUBLIC:
            if not c.get(k) and k != "result":
                errs.append(f'{path}: {c.get("id")}: пустое {k}')
            texts.append((f'{c.get("id")}.{k}', str(c.get(k) or "")))
    for where, t in texts:
        for rx, why in BAD:
            m = rx.search(t)
            if m:
                errs.append(f"{path}: {where}: {why}: «{m.group(0).strip()}»")
    return errs


def image(rel, slug, stage):
    if not rel:
        return None
    src = os.path.join(HERE, rel)
    if not os.path.isfile(src):
        raise SystemExit(f"нет картинки {rel}")
    im = Image.open(src)
    name = os.path.basename(rel)
    dst = os.path.join(stage, ASSETS, slug)
    os.makedirs(dst, exist_ok=True)
    shutil.copy2(src, os.path.join(dst, name))
    return {"src": f"/assets/neprosto/cases/{slug}/{name}", "w": im.size[0], "h": im.size[1]}


def payload(d, stage):
    slug = d["portfolio"].rstrip("/").split("/")[-1]
    out = {"name": d.get("name", ""), "site": d.get("site", ""), "tags": d.get("tags") or [], "css_v": CSS_V,
           "metric": {k: d["metric"][k] for k in ("value", "label")} if d.get("metric") else None, "cases": []}
    for c in d.get("cases") or []:
        if c.get("show") is False:
            continue
        out["cases"].append({**{k: c.get(k) for k in ("id", "date", "type") + PUBLIC},
                             "before": image(c.get("before"), slug, stage), "after": image(c.get("after"), slug, stage)})
    out["cases"].sort(key=lambda c: str(c.get("date") or ""), reverse=True)  # от свежих к старым
    return slug, out


def ssh(args, data=None):
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20"]
    if os.path.isfile(KEY):
        cmd += ["-i", KEY]
    r = subprocess.run(cmd + [HOST] + args, input=data, capture_output=True, timeout=180)
    if r.returncode:
        raise SystemExit("ssh: " + r.stderr.decode("utf-8", "replace"))
    return r.stdout.decode("utf-8", "replace")


REFRESH = """<?php define("MODX_API_MODE", true); require "%s/public_html/index.php";
$modx->cacheManager->refresh(); echo "cache refreshed\\n";""" % HOME


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clients", nargs="*")
    ap.add_argument("--all", action="store_true", help="все yml с publish: true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true", help="выложить, даже если не менялось")
    a = ap.parse_args()
    files = sorted(f for f in os.listdir(HERE) if f.endswith(".yml"))
    docs, errs = {}, []
    for f in files:
        d = yaml.safe_load(open(os.path.join(HERE, f), encoding="utf-8"))
        docs[f[:-4]] = d
        errs += lint(d, f)
    pick = a.clients or ([k for k, d in docs.items() if d.get("publish")] if a.all else [])
    for k in pick:
        if k not in docs:
            raise SystemExit(f"нет cases/{k}.yml")
    bad = [e for e in errs if any(e.startswith(k + ".yml") for k in pick)]
    for e in errs:
        print(("ОШИБКА " if e in bad else "внимание ") + e)
    if bad:
        raise SystemExit("публикация остановлена: исправьте ошибки выше")
    if not pick:
        print(f"проверено {len(files)} yml; выкладывать: укажите клиентов или --all")
        return
    state = json.load(open(STATE)) if os.path.isfile(STATE) else {}
    stage = tempfile.mkdtemp(prefix="np-cases-")
    try:
        os.makedirs(os.path.join(stage, "np-cases"))
        os.makedirs(os.path.join(stage, ASSETS), exist_ok=True)
        shutil.copy2(os.path.join(HERE, "modx", "cases.css"), os.path.join(stage, ASSETS, "cases.css"))
        changed = []
        for k in pick:
            slug, out = payload(docs[k], stage)
            body = json.dumps(out, ensure_ascii=False, indent=1)
            h = hashlib.sha256(body.encode()).hexdigest()
            open(os.path.join(stage, "np-cases", slug + ".json"), "w", encoding="utf-8").write(body)
            print(f"{k} → {slug}.json: {len(out['cases'])} мини-кейсов, метрика: {bool(out['metric'])}")
            if state.get(slug) != h or a.force:
                changed.append((slug, h))
        if not a.apply:
            print("сухой прогон, файлы:", stage)
            return
        if not changed:
            print("без изменений")
            return
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as t:  # только файлы: записи каталогов поменяли бы права ~/ne-prosto
            for root, _, fs in os.walk(stage):
                for f in fs:
                    p = os.path.join(root, f)
                    t.add(p, arcname=os.path.relpath(p, stage).replace(os.sep, "/"), recursive=False)
        print(ssh([f"tar -C {HOME} -xf - && chmod 600 {HOME}/np-cases/*.json && echo uploaded"], buf.getvalue()).strip())
        print(ssh(["php"], REFRESH.encode()).strip())
        for slug, h in changed:
            state[slug] = h
        json.dump(state, open(STATE, "w"), indent=1)
    finally:
        if a.apply:
            shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    main()
