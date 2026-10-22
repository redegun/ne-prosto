<?php
// task 547: тексты политики (113) и согласия (114) — черновики #543 этапа 1, реквизиты ИП Ветрова, почта ne-prosto
define('MODX_API_MODE', true);
require '/home/r/redegun/ne-prosto/public_html/index.php';
$dir = __DIR__; $mode = $argv[1] ?? 'dry';
@mkdir("$dir/before");
$map = [113 => ['policy.html', 'Политика в отношении обработки персональных данных', 'Политика в отношении обработки персональных данных посетителей сайта ne-prosto.ru: какие данные обрабатываем, зачем, сколько храним и как отозвать согласие.'],
        114 => ['consent.html', 'Согласие на обработку персональных данных', 'Согласие на обработку персональных данных, которое посетитель даёт, отправляя форму на сайте ne-prosto.ru.']];
foreach ($map as $id => [$f, $lt, $desc]) {
  $r = $modx->getObject('modResource', $id); if (!$r) die("no $id\n");
  if (!file_exists("$dir/before/res$id.json")) file_put_contents("$dir/before/res$id.json", json_encode($r->toArray(), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
  echo "$id {$r->uri} tpl={$r->template} len=" . mb_strlen($r->content) . " -> " . mb_strlen(file_get_contents("$dir/$f")) . "\n";
  if ($mode !== 'apply') continue;
  $r->set('content', file_get_contents("$dir/$f")); $r->set('longtitle', $lt); $r->set('description', $desc); $r->set('editedon', time());
  if (!$r->save()) die("save $id failed\n");
}
if ($mode === 'apply') { $modx->cacheManager->refresh(); echo "applied\n"; }
