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
$checks = [];
// Départ B00 public réel sur un seul numéro fictif ; aucun reseed global.
(static function () use (&$checks): void {
    $manifest = get_option('imagine_demo_manifest');
    $slug = 'demo-2026-t4';
    $issue = (int) $manifest[$slug];
    $media = (int) $manifest[$slug . '-pdf'];
    if (get_post_meta($issue, 'imagine_demo_key', true) !== $slug
        || get_post_meta($media, 'imagine_demo_key', true) !== $slug . '-pdf') {
        throw new RuntimeException('Propriétaire fixture C11 incohérent.');
    }
    $sourcePath = '/var/www/imagine-private-pdf/source/' . $slug . '.pdf';
    $bytes = file_get_contents($sourcePath);
    $privatePath = \Imagine\Site\PdfNumero::path($issue);
    $paths = [wp_upload_dir()['basedir'] . '/imagine-demo/' . $slug . '.pdf',
        WP_CONTENT_DIR . '/imagine-demo-build/assets/' . $slug . '.pdf'];
    $title = get_post($media)->post_title;
    try {
        foreach ($paths as $path) {
            if (file_exists($path) || is_link($path) || file_put_contents($path, $bytes) !== strlen($bytes)) {
                throw new RuntimeException('Départ public fictif C11 impossible.');
            }
        }
        wp_update_post(['ID' => $media, 'post_status' => 'inherit', 'guid' => content_url('/uploads/imagine-demo/' . $slug . '.pdf')]);
        update_attached_file($media, $paths[0]);
        $checks['depart_deux_copies_publiques'] = is_file($paths[0]) && is_file($paths[1])
            && get_post($media)->post_status === 'inherit';
        for ($i = 1; $i <= 2; $i++) {
            $id = \Imagine\Demo\Seed\media($slug . '-pdf', $slug . '.pdf', 'application/pdf', $title);
            clearstatcache();
            $checks['passage_' . $i . '_copies_supprimees'] = !file_exists($paths[0]) && !is_link($paths[0])
                && !file_exists($paths[1]) && !is_link($paths[1]);
            $checks['passage_' . $i . '_ids_octets_prives_stables'] = $id === $media
                && (int) get_post_meta($issue, 'imagine_pdf_id', true) === $media
                && \Imagine\Site\PdfNumero::path($issue) === $privatePath
                && file_get_contents($privatePath) === $bytes && get_post($media)->post_status === 'private'
                && !get_post_meta($media, '_wp_attached_file', true);
        }
    } finally {
        foreach ($paths as $path) {
            if ((file_exists($path) || is_link($path)) && !unlink($path)) {
                throw new RuntimeException('Nettoyage du témoin public C11 refusé.');
            }
        }
        \Imagine\Site\PdfNumero::protect($issue, $media, $sourcePath);
    }
    $checks['restauration_privee_relue'] = get_post($media)->post_status === 'private'
        && file_get_contents(\Imagine\Site\PdfNumero::path($issue)) === $bytes
        && !file_exists($paths[0]) && !file_exists($paths[1]);
})();
echo wp_json_encode($checks);
if (in_array(false, $checks, true)) {
    WP_CLI::halt(1);
}
