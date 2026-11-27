<?php

declare(strict_types=1);

// Executed only by b12.py inside a rolled-back native WordPress transaction.
use Imagine\Site\IntegrationsCorps;
use Imagine\Site\Medias;

$checks = [];
$events = [];
$transport = 0;
$phase = 'boot';
$check = static function (string $name, bool $ok) use (&$checks, &$events): void {
    $checks[$name] = $ok;
    if (!$ok) {
        throw new RuntimeException('B12: ' . $name . ' events=' . wp_json_encode($events));
    }
};
$observe = static function ($pre, $args, $url) use (&$events, &$phase) {
    $events[] = ['phase' => $phase, 'url' => $url, 'blocked' => is_wp_error($pre) && $pre->get_error_code() === 'imagine_demo_offline'];
    return $pre;
};
$debug = static function () use (&$transport): void { $transport++; };
add_filter('pre_http_request', $observe, PHP_INT_MAX, 3);
add_action('http_api_debug', $debug);
$mutant = !empty($GLOBALS['b12_mutant']);
if ($mutant && class_exists(IntegrationsCorps::class)) {
    wp_embed_unregister_handler('imagine_corps_externe', PHP_INT_MIN);
    remove_filter('pre_oembed_result', [IntegrationsCorps::class, 'resolution'], PHP_INT_MAX);
    remove_filter('pre_render_block', [IntegrationsCorps::class, 'bloc'], PHP_INT_MAX);
    remove_filter('rest_dispatch_request', [IntegrationsCorps::class, 'apercu'], PHP_INT_MAX);
}
$editor = get_users(['role' => 'administrator', 'number' => 1])[0];
wp_set_current_user($editor->ID);
$fixture = get_option('imagine_b11_fixture');
$check('fixture_fictive_existante', !empty($fixture['fictif']) && get_post((int) $fixture['issue']) !== null);
$url = 'https://www.youtube.com/watch?v=B12FICTIF01';
$body = ["Texte fictif C:\\B12.\n\n" . $url . "\n", '<!-- wp:embed {"url":"' . $url . '","type":"video","providerNameSlug":"youtube"} -->' . "\n" . '<figure class="wp-block-embed"><div class="wp-block-embed__wrapper">' . "\n" . $url . "\n" . '</div></figure>' . "\n" . '<!-- /wp:embed -->'];
$ids = [];
$renderings = [];
foreach ($body as $i => $content) {
    $phase = 'save_' . $i;
    $id = wp_insert_post(wp_slash(['post_type' => 'post', 'post_status' => 'publish', 'post_title' => 'B12 ESSAI FICTIF TEMPORAIRE ' . $i, 'post_content' => $content, 'post_author' => $editor->ID, 'meta_input' => ['imagine_numero_id' => (int) $fixture['issue'], 'imagine_reserve' => false]]), true);
    $check('article_' . $i . '_cree', !is_wp_error($id) && $id > 0);
    $ids[] = $id;
    $GLOBALS['post'] = get_post($id);
    global $wp_embed;
    $wp_embed->cache_oembed($id); // Actual native post-save AJAX target, not a synthetic resolver.
    $check('corps_' . $i . '_exact_save', get_post($id)->post_content === $content);
    $phase = 'render_' . $i;
    if ($mutant) {
        $wp_embed->delete_oembed_caches($id);
    }
    $renderings[$i] = apply_filters('the_content', $content);
    $phase = 'preview_' . $i;
    $request = new WP_REST_Request('GET', '/oembed/1.0/proxy');
    $request->set_param('url', $url . '&b12=' . $i);
    $response = rest_do_request($request);
    $check('route_' . $i . '_executee', $response instanceof WP_REST_Response && !in_array($response->get_status(), [401, 403], true));
    if (!$mutant) {
        $html = (array) $response->get_data();
        $check('apercu_' . $i . '_lien', isset($html['html']) && str_contains($html['html'], '<a href=') && !preg_match('/<(iframe|script|img)\b/i', $html['html']));
        $check('rendu_' . $i . '_lien', str_contains($renderings[$i], '<a href=') && str_contains(html_entity_decode($renderings[$i]), $url) && !preg_match('/<(iframe|script|img)\b/i', $renderings[$i]));
    }
    $check('corps_' . $i . '_exact_apres', get_post($id)->post_content === $content);
}
if ($mutant) {
    foreach (['save', 'render', 'preview'] as $surface) {
        $found = array_filter($events, static fn ($e) => str_starts_with($e['phase'], $surface . '_'));
        $check('mutation_' . $surface . '_tentative', count($found) > 0);
    }
    $check('mutation_B00_avant_transport', count($events) > 0 && !in_array(false, array_column($events, 'blocked'), true) && $transport === 0);
} else {
    $check('zero_tentative_save_render_preview', $events === []);
    foreach (['0', '1'] as $setting) {
        update_option(Medias::OPTION, ['hosts' => [], 'integration' => $setting], false);
        foreach ($ids as $i => $id) {
            $GLOBALS['post'] = get_post($id);
            $phase = 'matrix_save_' . $setting . '_' . $i;
            wp_update_post(wp_slash(['ID' => $id, 'post_content' => $body[$i]]));
            $wp_embed->cache_oembed($id);
            $check('matrix_corps_exact_' . $setting . '_' . $i, get_post($id)->post_content === $body[$i]);
            $phase = 'matrix_render_' . $setting . '_' . $i;
            $html = apply_filters('the_content', $body[$i]);
            $check('matrix_rendu_lien_' . $setting . '_' . $i, str_contains($html, '<a href=') && !preg_match('/<(iframe|script|img)\\b/i', $html));
            $phase = 'matrix_preview_' . $setting . '_' . $i;
            $request = new WP_REST_Request('GET', '/oembed/1.0/proxy');
            $request->set_param('url', $url . '&setting=' . $setting . '&i=' . $i);
            $data = (array) rest_do_request($request)->get_data();
            $check('matrix_apercu_lien_' . $setting . '_' . $i, isset($data['html']) && str_contains($data['html'], '<a href=') && !isset($data['thumbnail_url']) && !preg_match('/<(iframe|script|img)\\b/i', $data['html']));
        }
        foreach ([$url, 'https://vimeo.com/123456789012', 'https://tiers-fictif.example.invalid/B12', 'https://example.invalid/fictif.mp4'] as $external) {
            $phase = 'shortcode_' . $setting;
            $GLOBALS['post'] = get_post($ids[0]);
            $html = $wp_embed->run_shortcode('[embed]' . $external . '[/embed]');
            $check('shortcode_' . $setting . '_' . md5($external), str_contains($html, '<a href=') && !preg_match('/<(iframe|script|img|video|audio)\b/i', $html));
            $check('direct_' . $setting . '_' . md5($external), str_contains((string) wp_oembed_get($external), '<a href='));
        }
    }
    // A stale successful native cache must not reintroduce third-party HTML.
    $GLOBALS['post'] = get_post($ids[0]);
    $wp_embed->post_ID = $ids[0];
    $attr = wp_parse_args([], wp_embed_defaults($url));
    $key = '_oembed_' . md5($url . serialize($attr));
    update_post_meta($ids[0], $key, '<iframe src="https://tiers-fictif.example.invalid/"></iframe>');
    $check('cache_ancien_ne_sort_pas', !str_contains($wp_embed->shortcode([], $url), '<iframe'));
    $cachedBlock = '<!-- wp:embed {"url":"' . $url . '"} --><figure><iframe src="https://tiers-fictif.example.invalid/"></iframe><script>alert(1)</script><img src="https://tiers-fictif.example.invalid/v.jpg"></figure><!-- /wp:embed -->';
    $check('bloc_enregistre_ancien_ne_sort_pas', !preg_match('/<(iframe|script|img)\b/i', do_blocks($cachedBlock)));
    $request = new WP_REST_Request('GET', '/oembed/1.0/proxy');
    $request->set_param('url', $url . '&cached=1');
    $request->sanitize_params();
    $args = $request->get_params();
    set_transient('oembed_' . md5(serialize($args)), (object) ['html' => '<iframe src="https://tiers-fictif.example.invalid/"></iframe>', 'thumbnail_url' => 'https://tiers-fictif.example.invalid/v.jpg'], 600);
    $data = (array) rest_do_request($request)->get_data();
    $check('proxy_cache_ancien_ne_sort_pas', isset($data['html']) && !preg_match('/<(iframe|script|img)\b/i', $data['html']) && !isset($data['thumbnail_url']));
    // Native internal content is compared against the same request with only B12 removed.
    $internal = get_permalink($ids[1]);
    $sentinel = '<p>INTERNE B12</p>';
    $check('interne_handler_delegue', IntegrationsCorps::lien([], [], $internal) === false);
    $check('interne_resolution_identique', IntegrationsCorps::resolution($sentinel, $internal) === $sentinel);
    $internalBlock = ['blockName' => 'core/embed', 'attrs' => ['url' => $internal], 'innerBlocks' => [], 'innerHTML' => $sentinel, 'innerContent' => [$sentinel]];
    $check('interne_bloc_identique', render_block($internalBlock) === $sentinel);
    $internalRequest = new WP_REST_Request('GET', '/oembed/1.0/proxy');
    $internalRequest->set_param('url', $internal);
    $with = rest_do_request($internalRequest)->get_data();
    remove_filter('rest_dispatch_request', [IntegrationsCorps::class, 'apercu'], PHP_INT_MAX);
    $without = rest_do_request($internalRequest)->get_data();
    add_filter('rest_dispatch_request', [IntegrationsCorps::class, 'apercu'], PHP_INT_MAX, 3);
    $normalize = static function ($data): string {
        $data = (array) $data;
        if (isset($data['html'])) {
            $data['html'] = preg_replace('/(?:(?<=data-secret=")|(?<=secret=))[a-zA-Z0-9]+/', 'NATIVE_RANDOM_SECRET', $data['html']);
        }
        return wp_json_encode($data);
    };
    $check('interne_proxy_natif_identique', !empty($with) && $normalize($with) === $normalize($without));
    $check('zero_tentative_tous_settings', $events === [] && $transport === 0);
}
foreach ($ids as $id) {
    wp_delete_post($id, true);
    $check('essai_' . $id . '_retire', get_post($id) === null);
}
remove_filter('pre_http_request', $observe, PHP_INT_MAX);
remove_action('http_api_debug', $debug);
echo wp_json_encode(['mutant' => $mutant, 'checks' => $checks, 'total' => count($checks), 'events' => $events, 'transport' => $transport, 'ids_removed' => $ids]);
