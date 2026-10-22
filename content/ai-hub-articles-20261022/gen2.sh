#!/bin/bash
cd /root/orch-tmp/task-503; mkdir -p img
style=$(cat style.txt)
for n in $(python3 -c 'import json;print(" ".join(json.load(open("prompts.json"))))'); do
  [ -s img/$n-orig.png ] && continue
  p=$(python3 -c "import json,sys;print(json.load(open('prompts.json'))['$n'])")
  ( timeout 420 openclaw infer image generate --prompt "$style
$p" --size 1536x1024 --output-format png --quality medium --output img/$n-orig.png --timeout-ms 400000 > img/$n.log 2>&1; echo "$n rc=$?" ) &
done
wait
ls -la img/
