<?php
// task 538: рендер неопубликованной статьи через движок (как живая страница) — для проверки и предпросмотра
// php render.php <id> <out.html>
define('MODX_API_MODE', true);
$_SERVER['HTTP_HOST'] = 'ne-prosto.ru'; $_SERVER['SERVER_PORT'] = 443; $_SERVER['HTTPS'] = 'on';
require '/home/r/redegun/ne-prosto/public_html/index.php';
$id = (int)$argv[1]; $outFile = $argv[2];
$modx->initialize('web');
$modx->config['site_url'] = 'https://ne-prosto.ru/'; $modx->config['http_host'] = 'ne-prosto.ru'; $modx->config['url_scheme'] = 'https://';
$modx->getRequest(); $modx->getParser();
$r = $modx->getObject('modResource', $id);
if (!$r || (int)$r->get('parent') !== 2) die("bad id\n");
$modx->resource = $r; $modx->resourceIdentifier = $id; $modx->resourceMethod = 'id';
$modx->elementCache = [];
$r->_output = $r->process();
$max = (int)$modx->getOption('parser_max_iterations', null, 10);
$modx->parser->processElementTags('', $r->_output, true, false, '[[', ']]', [], $max);
$modx->parser->processElementTags('', $r->_output, true, true, '[[', ']]', [], $max);
if ($modx->sjscripts) $r->_output = preg_replace('~(</head>)~i', implode("\n", $modx->sjscripts) . "\n\\1", $r->_output, 1);
if ($modx->jscripts) $r->_output = preg_replace('~(</body>)(?!.*</body>)~is', implode("\n", $modx->jscripts) . "\n\\1", $r->_output, 1);
$modx->invokeEvent('OnWebPagePrerender');
file_put_contents($outFile, $r->_output);
echo "$id ".strlen($r->_output)."\n";
