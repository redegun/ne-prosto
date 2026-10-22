<?php
// task 538: переносит блок-призыв из конца текста статьи (сниппет npArticleCta &pos=`mid`) перед N-м H2 текста.
// Меньше двух H2 — средний блок не показываем (останется только блок в конце).
if ($modx->event->name !== 'OnWebPagePrerender' || !$modx->resource) return;
$out = &$modx->resource->_output;
if (strpos($out, 'np-cta-slot-end') === false) return;
if (!preg_match('~<div class="np-cta-slot" data-np-cta-place="(\d+)">(.*?)</div><i class="np-cta-slot-end"></i>~s', $out, $m, PREG_OFFSET_CAPTURE)) return;
$slotAt = $m[0][1];
$start = strpos($out, 'class="article-content"');
$out = substr_replace($out, '', $slotAt, strlen($m[0][0]));
if ($start === false || $start > $slotAt) return;
preg_match_all('~<h2[\s>]~', substr($out, $start, $slotAt - $start), $h, PREG_OFFSET_CAPTURE);
$n = count($h[0]);
if ($n < 2) return;
$k = max(1, min((int)$m[1][0], $n) - 1);
$out = substr_replace($out, $m[2][0], $start + $h[0][$k][1], 0);
