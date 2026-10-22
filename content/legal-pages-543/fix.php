<?php
// task 543 fix: скрытое пустое policy перед галочкой — иначе FormIt не проверяет отсутствующее поле
define('MODX_API_MODE', true);
require '/home/r/redegun/ne-prosto/public_html/index.php';
$a = '<label class="np-consent__label"><input type="checkbox" name="policy"';
foreach ([93, 106, 42] as $id) {
  $o = $modx->getObject('modChunk', $id); $c = $o->get('snippet');
  if (strpos($c, '<input type="hidden" name="policy"') !== false) { echo "$id already\n"; continue; }
  if (substr_count($c, $a) !== 1) die("anchor $id\n");
  $o->set('snippet', str_replace($a, '<input type="hidden" name="policy" value="">' . $a, $c)); $o->save(); echo "$id fixed\n";
}
$modx->cacheManager->refresh();
