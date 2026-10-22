<?php
// task 503: crosslinks 1->2, 1->8 in resource 104; "Полезно почитать" block in resource 103
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$dir = __DIR__; $mode = $argv[1] ?? "dry"; $B = "https://ne-prosto.ru/blog/";
// 104
$r = $modx->getObject("modResource", 104); $c = $r->get("content");
if (!file_exists("$dir/r104.before.html")) file_put_contents("$dir/r104.before.html", $c);
if (strpos($c, "skorost-otveta-na-zayavku") === false) {
  $a = "посчитайте чаты, где клиенту так никто и не ответил.";
  $p = strpos($c, $a); if ($p === false) die("104 anchor1 not found\n");
  $c = substr_replace($c, $a." Как перевести такую проверку в цифры, мы разобрали в статье <a href=\"{$B}kak-poschitat-poteryannye-zayavki\">как посчитать, сколько заявок вы теряете</a>.", $p, strlen($a));
  $a = "приходит, когда выбор почти сделан.";
  $p = strpos($c, $a); if ($p === false) die("104 anchor2 not found\n");
  $c = substr_replace($c, $a." Подробнее о том, как <a href=\"{$B}skorost-otveta-na-zayavku\">скорость ответа на заявку</a> влияет на продажи, читайте в отдельной статье.", $p, strlen($a));
  echo "104 links prepared\n";
  if ($mode === "apply") { $r->set("content", $c); $r->save(); echo "104 saved\n"; }
} else echo "104 already linked\n";
// 103
$r = $modx->getObject("modResource", 103); $c = $r->get("content");
if (!file_exists("$dir/r103.before.html")) file_put_contents("$dir/r103.before.html", $c);
if (strpos($c, "Полезно почитать") === false) {
  $L = [
   ["chat-bot-ili-ii-assistent","Чат-бот или ассистент с одобрением менеджера: что выбрать малому бизнесу"],
   ["kuda-propadayut-zayavki-iz-messendzherov","Куда пропадают заявки из мессенджеров, пока менеджер занят"],
   ["oshibki-vnedreniya-ii-v-biznes","Ошибки при внедрении ИИ в бизнес: цены, обещания, запретные темы"],
   ["skorost-otveta-na-zayavku","Скорость ответа на заявку: как она влияет на продажи"],
   ["kak-poschitat-poteryannye-zayavki","Как посчитать, сколько заявок вы теряете"],
   ["vse-obrashheniya-v-odnom-okne","Все обращения в одном окне: чем это отличается от CRM"],
   ["zapisi-zvonkov-dlya-ii-assistenta","Как записи звонков учат ассистента отвечать как лучший менеджер"],
   ["chto-sprosit-u-klienta-pri-pervom-obrashhenii","Чек-лист: что спросить у клиента при первом обращении"],
   ["novyj-ili-postoyannyj-klient","Новый или постоянный клиент: зачем это понимать с первого сообщения"],
  ];
  $h = "<section><h2>Полезно почитать</h2><ul>";
  foreach ($L as [$a, $t]) $h .= "<li><a href=\"{$B}$a\">$t</a></li>";
  $h .= "</ul></section>";
  $a = "<section><h2>Частые вопросы</h2>"; $p = strpos($c, $a); if ($p === false) die("103 anchor not found\n");
  $c = substr($c, 0, $p).$h.substr($c, $p);
  echo "103 block prepared\n";
  if ($mode === "apply") { $r->set("content", $c); $r->save(); echo "103 saved\n"; }
} else echo "103 already has block\n";
$modx->cacheManager->refresh();
