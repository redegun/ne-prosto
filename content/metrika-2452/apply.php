<?php
// task 2452: вернуть Яндекс Метрику 27066311 на ne-prosto.ru (чанки head, head_2019) + цели форм + политика 113 (раздел cookies)
// dry run по умолчанию; применение — NP_APPLY=1 или файл _agent_archives/task2452/APPLY = yes
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task2452"; @mkdir($bk, 0700, true);
$apply = getenv("NP_APPLY") === "1" || trim((string)@file_get_contents("$bk/APPLY")) === "yes";
function g($c, $m) { if (!$c) { echo "GUARD FAIL: $m\n"; exit(1); } }

$SNIP = <<<'HTML'
<!-- Yandex.Metrika counter (task 2452) -->
<script type="text/javascript">
(function(m,e,t,r,i,k,a){ m[i]=m[i]||function(){ (m[i].a=m[i].a||[]).push(arguments) };m[i].l=1*new Date();for(var j=0;j<document.scripts.length;j++){ if(document.scripts[j].src===r){ return; } }k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a) })(window,document,"script","https://mc.yandex.ru/metrika/tag.js?id=27066311","ym");
ym(27066311,"init",{ ssr:true,webvisor:true,clickmap:true,accurateTrackBounce:true,trackLinks:true,trackHash:true });
/* цели: AjaxForm шлёт $(document).trigger("af_complete"); jQuery зовёт и document.onaf_complete, какой бы экземпляр jQuery ни был на странице */
document.onaf_complete=function(e,r){ try{ if(r&&r.success){ var w=r.form&&r.form.closest?r.form.closest(".jobs__form"):null;ym(27066311,"reachGoal",w&&w.length?"job_form":"lead_form"); } }catch(x){ } };
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/27066311" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->
HTML;
$SNIP = rtrim($SNIP, "\n");
g(strpos($SNIP, "[[") === false && strpos($SNIP, "]]") === false, "snippet has no MODX tags");
g(!preg_match('/\{\S/', $SNIP), "snippet: every { followed by whitespace (Fenom-safe)");

// --- чанки
$want = [
  "head" => "a36c44842e98acba0cd6ab5137b1c4b96a2435156b835d7c6515772fff91972a",
  "head_2019" => "6aabe95c62b361d9406a61c7e7b13baf15f4a879dd43a47fb9cb345c810986bf",
];
$chunks = [];
foreach ($want as $n => $h) {
  $o = $modx->getObject("modChunk", ["name" => $n]);
  g($o, "$n exists");
  $v = $o->get("snippet");
  g(hash("sha256", $v) === $h, "$n sha");
  g(!preg_match('/mc\.yandex|ym\(|yaCounter/i', $v), "$n has no metrika yet");
  if ($n === "head_2019") {
    g(substr_count($v, "</head>") === 1, "head_2019 has one </head>");
    $nv = str_replace("</head>", $SNIP . "\n</head>", $v);
  } else {
    $nv = rtrim($v, "\n") . "\n" . $SNIP . "\n";
  }
  g(substr_count($nv, "ym(27066311") === 2, "$n new has init+goal");
  $chunks[$n] = [$o, $v, $nv];
}

// рендер сниппета парсером MODX/pdoTools: не должен измениться
$parser = $modx->getParser();
$s = $SNIP;
$parser->processElementTags("", $s, true, false, "[[", "]]", [], 10);
$parser->processElementTags("", $s, true, true, "[[", "]]", [], 10);
g($s === $SNIP, "modParser keeps snippet");
echo "parser class: ", get_class($parser), " fenom_parser=", var_export($modx->getOption("pdotools_fenom_parser"), true), " fenom_default=", var_export($modx->getOption("pdotools_fenom_default"), true), "\n";
if ($pdo = $modx->getService("pdoTools")) {
  $r = $pdo->getChunk("@INLINE " . $SNIP, []);
  g(trim($r) === trim($SNIP), "pdoTools getChunk keeps snippet");
  echo "pdoTools render ok\n";
}

// --- политика 113
$p = $modx->getObject("modResource", 113);
g($p, "res 113");
$pc = (string)$p->get("content");
g(hash("sha256", $pc) === "0e9c99c38a34143f7d31363aa2ddbe2a248ab36451ceb3013860d3efbe1f1d94", "113 sha");
$rep = [
  "<p>Редакция от 22.10.2026</p>" => "<p>Редакция от 14.11.2026</p>",
  "<li>технические данные: IP-адрес, данные браузера, дата и время обращения (журналы сервера хостинга).</li>" =>
    "<li>технические данные: IP-адрес, данные браузера, дата и время обращения (журналы сервера хостинга);</li>\n<li>данные о посещениях, которые собирает Яндекс Метрика: cookies, сведения об устройстве и браузере, просмотренные страницы и действия на сайте (подробнее — раздел 7).</li>",
  "<li>рассмотреть отклик на вакансию и связаться с кандидатом.</li>" =>
    "<li>рассмотреть отклик на вакансию и связаться с кандидатом;</li>\n<li>вести статистику посещений и заявок, чтобы улучшать сайт.</li>",
  "<p>5.3. Третьим лицам данные не передаются, кроме случаев, предусмотренных законом.</p>" =>
    "<p>5.3. Третьим лицам данные не передаются, кроме случаев, предусмотренных законом. Данные о посещениях из раздела 7 обрабатывает сервис Яндекс Метрика (ООО «Яндекс»).</p>",
  "<p>Сайт использует технические cookies, нужные для работы форм. Сервисы веб-аналитики не используются. На странице «Координаты» показана Яндекс Карта: сервис Яндекса может устанавливать свои cookies.</p>" =>
    "<p>Сайт использует технические cookies, нужные для работы форм, и сервис веб-аналитики Яндекс Метрика (ООО «Яндекс»). Метрика ставит свои cookies и собирает обезличенные данные: IP-адрес, сведения об устройстве и браузере, откуда вы пришли, какие страницы открывали, как прокручивали их и что нажимали, отправили ли форму. По этим данным мы считаем посещения и заявки и улучшаем сайт. Яндекс обрабатывает эти данные по своей <a href=\"https://yandex.ru/legal/confidential/\" target=\"_blank\" rel=\"noopener\">политике конфиденциальности</a>.</p>\n<p>Чтобы Метрика не собирала данные, запретите cookies в настройках браузера или установите <a href=\"https://yandex.ru/support/metrica/general/opt-out.html\" target=\"_blank\" rel=\"noopener\">блокировщик Яндекс Метрики</a>. На странице «Координаты» показана Яндекс Карта: сервис Яндекса может устанавливать свои cookies.</p>",
];
$npc = $pc;
foreach ($rep as $a => $b) { g(substr_count($npc, $a) === 1, "113 anchor: " . mb_substr($a, 0, 60)); $npc = str_replace($a, $b, $npc); }
g(strpos($npc, "веб-аналитики не используются") === false, "113 no 'no analytics'");

// согласие 114 — только показать, не трогаем
$c = $modx->getObject("modResource", 114);
foreach (preg_split('/(?<=[.!?;])\s+/u', strip_tags((string)$c->get("content"))) as $sent) if (preg_match('/cookie|аналит|метрик/ui', $sent)) echo "114: ", trim($sent), "\n";

foreach ($chunks as $n => [$o, $v, $nv]) echo "$n new sha ", hash("sha256", $nv), "\n";
echo "113 new sha ", hash("sha256", $npc), "\n";
echo "guards ok\n";
if (!$apply) { echo "dry run\n"; exit(0); }

foreach ($chunks as $n => [$o, $v, $nv]) file_put_contents("$bk/$n.before.html", $v);
file_put_contents("$bk/res113.before.html", $pc);
file_put_contents("$bk/res113.before.json", json_encode(["editedon" => $p->get("editedon"), "editedby" => $p->get("editedby")]));
foreach ($chunks as $n => [$o, $v, $nv]) { $o->set("snippet", $nv); g($o->save(), "save $n"); }
$p->set("content", $npc); $p->set("editedon", time()); g($p->save(), "save 113");
$modx->cacheManager->refresh();
$out = [];
foreach ($chunks as $n => $_) { $v = $modx->getObject("modChunk", ["name" => $n])->get("snippet"); $out[$n] = hash("sha256", $v); file_put_contents("$bk/$n.after.html", $v); }
$v = (string)$modx->getObject("modResource", 113)->get("content"); $out["res113"] = hash("sha256", $v); file_put_contents("$bk/res113.after.html", $v);
file_put_contents("$bk/after.json", json_encode($out, JSON_PRETTY_PRINT));
@unlink("$bk/APPLY");
echo "APPLIED ", json_encode($out, JSON_PRETTY_PRINT), "\n";
