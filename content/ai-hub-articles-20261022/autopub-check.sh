#!/usr/bin/env bash
# task #528: ночная автопубликация статей хаба ne-prosto (MODX pub_date 04:00 МСК, 23–30.10.2026).
# 04:02 МСК: запрос на сайт запускает публикацию MODX, затем проверка, что статья дня отдаёт 200.
declare -A DAY=( [2026-10-23]=skorost-otveta-na-zayavku [2026-10-24]=vse-obrashheniya-v-odnom-okne
  [2026-10-25]=chat-bot-ili-ii-assistent [2026-10-26]=zapisi-zvonkov-dlya-ii-assistenta
  [2026-10-27]=novyj-ili-postoyannyj-klient [2026-10-28]=chto-sprosit-u-klienta-pri-pervom-obrashhenii
  [2026-10-29]=kak-poschitat-poteryannye-zayavki [2026-10-30]=oshibki-vnedreniya-ii-v-biznes )
a=${DAY[$(TZ=Europe/Moscow date +%F)]}; [ -n "$a" ] || exit 0
curl -s -o /dev/null --max-time 30 https://ne-prosto.ru/; sleep 5
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "https://ne-prosto.ru/blog/$a")
echo "$(date -Is) $a $code"
[ "$code" = 200 ] || bash /root/.openclaw/workspace/scripts/infra/alert.sh "ne-prosto #528: статья /blog/$a не вышла по расписанию (HTTP $code). Проверить pub_date в MODX."
