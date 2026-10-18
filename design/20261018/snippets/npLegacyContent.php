$id = (int) $modx->resource->get('id');
if ($id === 29) {
    return $modx->getChunk('page__heading') . '<div class="np-legacy-team">' . $modx->getChunk('np_team') . '</div>';
}
if ($id === 14) {
    return $modx->getChunk('page__heading') . '<ol class="jobs">' . $modx->runSnippet('pdoResources', [
        'parents' => 14, 'resources' => '-56', 'includeTVs' => 'requirements',
        'includeContent' => 1, 'tpl' => 'jobs__item', 'totalVar' => 'jobs_total', 'limit' => 0
    ]) . '</ol>';
}
if ($id === 56) {
    return $modx->getChunk('page__heading') . '<p class="page__text">Уточните задачи и условия работы у команды студии.</p><a href="/koordinatyi#request" class="np-button">Связаться со студией ↗</a>';
}
return $modx->runSnippet('content');