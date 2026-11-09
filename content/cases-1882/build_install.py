import json, hashlib, base64, sys
live = json.load(open('../live.json', encoding='utf-8'))
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
D = {
  "np_sha": sha(live["np_project"]),
  "np_anchor": "<p>{$introtext | notags}</p>",
  "np_call": "{$_modx->runSnippet('npCases', ['mode' => 'card', 'uri' => $uri])}",
  "res": {
    "84": {"uri": "portfolio/kppf", "sha": sha(live["res84"]), "anchor": '<p><a href="https://kppf.ru/" target="_blank" rel="noopener nofollow"'},
    "85": {"uri": "portfolio/merci", "sha": sha(live["res85"]), "anchor": '<p><a href="https://mercibeautysalon.ru/" target="_blank" rel="noopener nofollow"'},
  },
  "res_call": "[[!npCases]]\n",
  "snippet": open('npCases.php', encoding='utf-8').read(),
}
assert live["np_project"].count(D["np_anchor"]) == 1
tpl = open('install.tpl.php', encoding='utf-8').read().replace('@@DATA@@', base64.b64encode(json.dumps(D, ensure_ascii=False).encode()).decode())
open('install.php', 'w', encoding='utf-8', newline='\n').write(tpl)
print('ok', D["np_sha"])
