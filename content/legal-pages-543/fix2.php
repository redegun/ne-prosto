<?php
// task 543 fix2: галочка в «Обсудить проект» между файлом и кнопкой (grid-areas), ссылки в тексте согласия переносятся по словам
define('MODX_API_MODE', true);
require '/home/r/redegun/ne-prosto/public_html/index.php';
$A = '/home/r/redegun/ne-prosto/public_html/assets/neprosto/design-20261018/site.css';
$css = file_get_contents($A);
if (strpos($css, 'task 543 fix2') !== false) die("already\n");
copy($A, __DIR__ . '/site.before-fix2.css');
$css .= "/* task 543 fix2 */\n.np-site .request-form{grid-template-areas:\"frmName frmMail\" \"frmTextarea frmTextarea\" \"frmAttach frmAttach\" \"frmConsent frmConsent\" \"frmSubmit frmSubmit\"}.np-site .request-form .form-field_consent{grid-area:frmConsent}.np-site .np-consent a{display:inline!important;white-space:normal}\n@media(max-width:700px){.np-site .request-form{grid-template-areas:\"frmName\" \"frmMail\" \"frmTextarea\" \"frmAttach\" \"frmConsent\" \"frmSubmit\"}}\n";
file_put_contents($A, $css);
foreach ([11, 89] as $id) { $o = $modx->getObject('modChunk', $id); $c = $o->get('snippet'); if (substr_count($c, 'site.css?v=10') !== 1) die("anchor $id\n"); $o->set('snippet', str_replace('site.css?v=10', 'site.css?v=11', $c)); $o->save(); }
$modx->cacheManager->refresh(); echo "ok\n";
