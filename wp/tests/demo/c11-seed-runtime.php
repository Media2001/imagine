<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new RuntimeException('Cible C11 refusée.');
}
// Réutiliser seulement les deux fonctions réelles du seed, pas son orchestration close.
$source = file_get_contents(WP_CONTENT_DIR . '/imagine-demo-build/b00-seed.php');
$start = strpos($source, 'function upsert(');
$end = strpos($source, "update_option('imagine_demo_site'", $start);
if ($start === false || $end === false) {
    throw new RuntimeException('Fonctions seed introuvables.');
}
eval('namespace Imagine\\Demo\\Seed;' . substr($source, $start, $end - $start));
$manifest = get_option('imagine_demo_manifest');
$checks = [];
foreach (['t1', 't2', 't3', 'hs', 't4'] as $suffix) {
    $slug = 'demo-2026-' . $suffix;
    $issue = (int) $manifest[$slug];
    $media = (int) $manifest[$slug . '-pdf'];
    $before = \Imagine\Site\PdfNumero::path($issue);
    $bytes = file_get_contents($before);
    for ($i = 0; $i < 2; $i++) {
        $id = \Imagine\Demo\Seed\media($slug . '-pdf', $slug . '.pdf', 'application/pdf', get_post($media)->post_title);
        $checks[$slug . ':idempotent-' . $i] = $id === $media
            && \Imagine\Site\PdfNumero::path($issue) === $before && file_get_contents($before) === $bytes
            && !file_exists(WP_CONTENT_DIR . '/uploads/imagine-demo/' . $slug . '.pdf')
            && !file_exists(WP_CONTENT_DIR . '/imagine-demo-build/assets/' . $slug . '.pdf');
    }
}
echo wp_json_encode($checks);
if (in_array(false, $checks, true)) {
    WP_CLI::halt(1);
}
