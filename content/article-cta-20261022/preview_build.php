<?php
// task 538: render/<id>.html -> _preview/<alias>.html (как prep_preview.php #525: плашка, noindex, ссылки между черновиками)
$dir = $argv[1];
$ids = [105 => 'chat-bot-ili-ii-assistent', 106 => 'oshibki-vnedreniya-ii-v-biznes', 107 => 'skorost-otveta-na-zayavku', 108 => 'kak-poschitat-poteryannye-zayavki', 109 => 'vse-obrashheniya-v-odnom-okne', 110 => 'zapisi-zvonkov-dlya-ii-assistenta', 111 => 'chto-sprosit-u-klienta-pri-pervom-obrashhenii', 112 => 'novyj-ili-postoyannyj-klient'];
$bar = '<div style="position:sticky;top:0;z-index:99999;background:#ffe14d;color:#111;font:600 15px/1.4 sans-serif;padding:10px 16px;text-align:center">Черновик — статья ещё не опубликована и видна только по этой ссылке. Форма в черновике не отправляется.</div>';
foreach ($ids as $id => $a) {
  $h = file_get_contents(__DIR__ . "/render/$id.html");
  if (substr_count($h, '<aside class="np-cta ') !== 2) die("$id: cta count\n");
  if (strpos($h, '[[') !== false) die("$id: raw tags\n");
  foreach ($ids as $b) $h = preg_replace('#href="(https://ne-prosto\.ru)?/blog/' . preg_quote($b, '#') . '/?"#', 'href="' . $b . '.html"', $h);
  $h = str_replace(['http://localhost/', 'minifyx/cache/styles_da39a3ee5e.css'], ['https://ne-prosto.ru/', 'minifyx/cache/styles_8d58812fbf.css'], $h);
  if (strpos($h, 'localhost') !== false) die("$id: localhost left
");
  $h = preg_replace('#<meta name="robots"[^>]*>#i', '', $h);
  $h = preg_replace('#<head([^>]*)>#i', '<head$1><meta name="robots" content="noindex, nofollow">', $h, 1);
  $h = preg_replace('#<body([^>]*)>#i', '<body$1>' . $bar, $h, 1);
  $h = str_replace('<button type="submit" name="send" value="1" class="np-cta-form__submit">Отправить</button>', '<button type="button" class="np-cta-form__submit" disabled>Отправить</button>', $h);
  file_put_contents("$dir/$a.html", $h); echo "ok $a\n";
}
