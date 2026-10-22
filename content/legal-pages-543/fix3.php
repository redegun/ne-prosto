<?php
define('MODX_API_MODE', true);
require '/home/r/redegun/ne-prosto/public_html/index.php';
$r = $modx->getObject('modResource', 113);
if ($r->get('longtitle') === '') die("already\n");
$r->set('longtitle', '');
$r->set('content', '<p><strong>Политика ИП Ветров А.А. в отношении обработки персональных данных</strong></p>' . "\n" . $r->get('content'));
$r->save(); $modx->cacheManager->refresh(); echo "ok\n";
