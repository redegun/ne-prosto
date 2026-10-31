#!/usr/bin/env bash
# IndexNow для ne-prosto.ru (#862): indexnow.sh <url> [url...]
# Ключ публичный по протоколу (лежит в корне сайта <key>.txt), не секрет.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
KEY=$(tr -d ' \n' < "$HERE/indexnow.key")
HOST=ne-prosto.ru
[ $# -ge 1 ] || { echo "usage: $0 <url>..." >&2; exit 64; }
live=$(curl -s --max-time 20 "https://$HOST/$KEY.txt" | tr -d ' \r\n')
[ "$live" = "$KEY" ] || { echo "INDEXNOW: FAIL key file https://$HOST/$KEY.txt not served"; exit 1; }
urls=$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "$@")
body="{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY.txt\",\"urlList\":$urls}"
rc=1
for ep in https://yandex.com/indexnow https://api.indexnow.org/indexnow; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 -H 'Content-Type: application/json; charset=utf-8' -d "$body" "$ep")
  echo "INDEXNOW $ep -> $code"
  case "$code" in 200|202) rc=0 ;; esac
done
exit $rc
