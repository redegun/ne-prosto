<?php
// task 5377: исправления по аудиту kb #5182 (ne-prosto.ru). Dry-run по умолчанию, применение — NP_APPLY=1.
define("MODX_API_MODE", true);
require "/home/r/redegun/ne-prosto/public_html/index.php";
$apply = getenv("NP_APPLY") === "1";
$root = "/home/r/redegun/ne-prosto/public_html/";
$bk = "/home/r/redegun/ne-prosto/_agent_archives/task5377"; @mkdir($bk, 0700, true);
function g($c, $m) { if (!$c) { echo "GUARD FAIL: $m\n"; exit(1); } }
function rep1($v, $old, $new, $cnt, $label) { g(substr_count($v, $old) === $cnt, "$label anchor count=" . substr_count($v, $old) . " want $cnt"); return str_replace($old, $new, $v); }

$NOIDX = '[[*noindex:default=`<meta name="robots" content="max-image-preview:large">`]]';
$ADD = "\n" . '<link rel="canonical" href="[[~[[*id]]?scheme=`full`]]">' . "\n"
     . '<link rel="icon" href="/favicon.ico" sizes="48x48">' . "\n"
     . '<link rel="icon" href="/favicon.svg" type="image/svg+xml">' . "\n"
     . '<link rel="icon" href="/favicon-192.png" type="image/png" sizes="192x192">' . "\n"
     . '<link rel="apple-touch-icon" href="/apple-touch-icon.png">';

$els = []; // [obj, field, before, after, label]
// 1. head-чанки: canonical + favicon (TECH-10, TECH-5, SEO-TECH-351)
foreach (["head" => "e45b705617bc0cc783059ce5b7a458b4690522980df6600c370d5c056b69a61b", "head_2019" => "c98449cf502b509684d14915daa0a680ab52aca5fa66ca7b72bebd8202a30c92"] as $n => $h) {
  $o = $modx->getObject("modChunk", ["name" => $n]); g($o, "chunk $n");
  $v = $o->get("snippet"); g(hash("sha256", $v) === $h, "$n sha");
  g(stripos($v, "canonical") === false && stripos($v, 'rel="icon"') === false, "$n already has canonical/icon");
  $els["chunk_$n"] = [$o, "snippet", $v, rep1($v, $NOIDX, $NOIDX . $ADD, 1, $n)];
}
// 2. alt обложки статьи (ImagePlus tpl, IMGALT-3)
$o = $modx->getObject("modChunk", ["name" => "page__image--big"]); $v = $o->get("snippet");
g(hash("sha256", $v) === "c6a8d659b8c9ce009f50398737c845712aed1c562c75b81868402fffbf20ccfd", "page__image--big sha");
$els["chunk_page__image--big"] = [$o, "snippet", $v, rep1($v, "alt='[[+alt]]'", 'alt="[[+alt:default=`[[*pagetitle:htmlent]]`]]"', 1, "page__image--big")];
// 3. alt карточек статей (np_article, np_related)
$o = $modx->getObject("modChunk", ["name" => "np_article"]); $v = $o->get("snippet");
g(hash("sha256", $v) === "b5d486a9f5cdb1ba5572d3b6af064caa8a66e253209d9ca36cc34413c0314958", "np_article sha");
$els["chunk_np_article"] = [$o, "snippet", $v, rep1($v, 'alt="" loading="lazy"', 'alt="{$pagetitle | htmlent}" loading="lazy"', 1, "np_article")];
$o = $modx->getObject("modChunk", ["name" => "np_related"]); $v = $o->get("snippet");
g(hash("sha256", $v) === "67397e49abcafa249014da3458824997f9205d92f4f9602bdc4d11cedb968cc5", "np_related sha");
$els["chunk_np_related"] = [$o, "snippet", $v, rep1($v, 'alt="" loading="lazy"', 'alt="{$pagetitle | htmlent}" loading="lazy"', 2, "np_related")];
// 4. alt иллюстрации услуги (template 8)
$o = $modx->getObject("modTemplate", 8); $v = $o->get("content");
g(hash("sha256", $v) === "63a230e44ebd1fc605d8f99c6db94bf671c8006df3350933b999de9acb7c836f", "tpl8 sha");
$els["tpl_8"] = [$o, "content", $v, rep1($v, 'alt="" loading="eager"', 'alt="Иллюстрация к услуге «[[*pagetitle]]»" loading="eager"', 7, "tpl8")];
// 5. sitemap: вернуть главную (скрыта из меню, pdoSitemap без showHidden её не выводит) (TECH-7)
$r27 = $modx->getObject("modResource", 27); $v = $r27->get("content");
g($v === "[[pdoSitemap?\r\n]]", "r27 content");
$els["res27_content"] = [$r27, "content", $v, "[[pdoSitemap?\r\n    &showHidden=`1`\r\n    &resources=`-6,-17,-27,-29,-60,-113,-114`\r\n]]"];

// 6. TV-значения: noindex у служебной /404 (SEO-TECH-323, #2163); рыба в отзывах (SEO-ONP-344, #5260)
$tvs = [];
$cur17 = $modx->getObject("modTemplateVarResource", ["tmplvarid" => 2, "contentid" => 17]);
g(!$cur17 || $cur17->value === "", "res17 noindex empty");
$tvs[] = [2, 17, $cur17 ? $cur17->value : "", '<meta name="robots" content="noindex, nofollow">'];
foreach ([37 => "тарантиновского", 39 => "FM модулятор", 70 => "Новый отзыв нового клиента"] as $id => $needle) {
  $x = $modx->getObject("modTemplateVarResource", ["tmplvarid" => 15, "contentid" => $id]); g($x, "opinion $id");
  g(mb_strpos($x->value, $needle) !== false, "opinion $id needle");
  $tvs[] = [15, $id, $x->value, ""];
}
// 7. файлы в корне: robots.txt + favicon
$robots0 = file_get_contents($root . "robots.txt"); g($robots0 === "User-agent: *\r\nAllow: /", "robots.txt content");
$robots1 = "User-agent: *\r\nAllow: /\r\n\r\nSitemap: https://ne-prosto.ru/sitemap.xml\r\n";
$files = [
  "favicon.ico" => "__FAVICON_ICO__",
  "favicon.svg" => "__FAVICON_SVG__",
  "favicon-192.png" => "__FAVICON_192__",
  "apple-touch-icon.png" => "__APPLE_TOUCH__",
];
foreach ($files as $f => $_) g(!file_exists($root . $f), "$f exists already");

// пробный рендер новых тегов
$parser = $modx->getParser();
foreach ([1, 19, 129, 17] as $id) {
  $r = $modx->getObject("modResource", $id); $modx->resource = $r; $modx->resourceIdentifier = $id; $modx->elementCache = [];
  $s = '<link rel="canonical" href="[[~[[*id]]?scheme=`full`]]">|[[+alt:default=`[[*pagetitle:htmlent]]`]]|Иллюстрация к услуге «[[*pagetitle]]»';
  $parser->processElementTags("", $s, true, false, "[[", "]]", [], 10);
  $parser->processElementTags("", $s, true, true, "[[", "]]", [], 10);
  echo "render $id => $s\n";
}
foreach ($els as $k => [$o, $f, $b, $a]) echo "$k: sha before ", substr(hash("sha256", $b), 0, 12), " after ", substr(hash("sha256", $a), 0, 12), " len ", strlen($b), "->", strlen($a), "\n";
foreach ($tvs as [$tv, $id, $b, $a]) echo "tv$tv res$id: ", mb_substr(strip_tags($b), 0, 50), " -> [", $a, "]\n";
echo "guards ok\n";
if (!$apply) { echo "dry run\n"; exit(0); }

// бэкап
$before = ["elements" => [], "tvs" => [], "robots" => $robots0];
foreach ($els as $k => [$o, $f, $b, $a]) { $before["elements"][$k] = ["class" => get_class($o), "id" => $o->id, "field" => $f, "value" => $b, "sha" => hash("sha256", $b)]; file_put_contents("$bk/$k.before.txt", $b); }
foreach ($tvs as [$tv, $id, $b, $a]) $before["tvs"][] = ["tmplvarid" => $tv, "contentid" => $id, "value" => $b];
file_put_contents("$bk/before.json", json_encode($before, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
file_put_contents("$bk/robots.txt.before", $robots0);
g(filesize("$bk/before.json") > 1000, "backup written");

// применение
foreach ($els as $k => [$o, $f, $b, $a]) { $o->set($f, $a); g($o->save(), "save $k"); }
foreach ($tvs as [$tv, $id, $b, $a]) {
  $r = $modx->getObject("modResource", $id);
  $tvo = $modx->getObject("modTemplateVar", $tv);
  $tvo->setValue($id, $a); g($tvo->save(), "tv$tv res$id");
}
g(file_put_contents($root . "robots.txt", $robots1) !== false, "robots write");
foreach ($files as $f => $b64) g(file_put_contents($root . $f, base64_decode($b64)) !== false, "write $f");
foreach ($files as $f => $_) @chmod($root . $f, 0644);
$modx->cacheManager->refresh();

// readback
$after = [];
foreach ($els as $k => [$o, $f, $b, $a]) { $cls = get_class($o); $x = $modx->getObject($cls, $o->id); $v = $x->get($f); $after[$k] = hash("sha256", $v); file_put_contents("$bk/$k.after.txt", $v); echo "$k readback ", $v === $a ? "OK" : "DIFF(trim?)", "\n"; }
foreach ($tvs as [$tv, $id, $b, $a]) { $x = $modx->getObject("modTemplateVarResource", ["tmplvarid" => $tv, "contentid" => $id]); echo "tv$tv res$id now [", $x ? $x->value : "(no row)", "]\n"; }
foreach ($files as $f => $_) $after["file_$f"] = md5_file($root . $f);
$after["robots"] = md5_file($root . "robots.txt");
file_put_contents("$bk/after.json", json_encode($after, JSON_PRETTY_PRINT));
echo json_encode($after, JSON_PRETTY_PRINT), "\n";
