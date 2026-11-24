<?php

declare(strict_types=1);

use Imagine\Site\PdfNumero;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new RuntimeException('Cible C11 refusée.');
}
$manifest = get_option('imagine_demo_manifest');
$out = [];
foreach (['t1', 't2', 't3', 'hs', 't4'] as $suffix) {
    $slug = 'demo-2026-' . $suffix;
    $issue = (int) $manifest[$slug];
    $media = (int) $manifest[$slug . '-pdf'];
    if (get_post_meta($issue, 'imagine_demo_key', true) !== $slug
        || get_post_meta($media, 'imagine_demo_key', true) !== $slug . '-pdf') {
        throw new RuntimeException('Propriétaire fixture C11 incohérent.');
    }
    PdfNumero::protect($issue, $media, '/var/www/imagine-private-pdf/source/' . $slug . '.pdf',
        [wp_upload_dir()['basedir'] . '/imagine-demo/' . $slug . '.pdf',
            WP_CONTENT_DIR . '/imagine-demo-build/assets/' . $slug . '.pdf']);
    $post = get_post($issue);
    $content = str_replace(content_url('/uploads/imagine-demo/' . $slug . '.pdf'), PdfNumero::url($issue), $post->post_content);
    if ($content !== $post->post_content) {
        wp_update_post(wp_slash(['ID' => $issue, 'post_content' => $content]));
    }
    $out[] = ['issue' => $issue, 'attachment' => $media,
        'private' => is_file(PdfNumero::path($issue)) && get_post($media)->post_status === 'private',
        'url' => wp_get_attachment_url($media)];
}
echo wp_json_encode($out);
