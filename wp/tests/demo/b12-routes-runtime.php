<?php

declare(strict_types=1);

// Native router + native proxy transient, rolled back by b12-corrections.py.
use Imagine\Site\IntegrationsCorps;

$checks = [];
$events = [];
$transport = 0;
$phase = 'boot';
$check = static function (string $key, bool $value) use (&$checks): void { $checks[$key] = $value; };
$observe = static function ($pre, $args, $url) use (&$events, &$phase) {
    $events[] = ['phase' => $phase, 'url' => $url, 'blocked' => is_wp_error($pre) && $pre->get_error_code() === 'imagine_demo_offline'];
    return $pre;
};
$debug = static function () use (&$transport): void { $transport++; };
$routes = ['/oembed/1.0/proxy', '/oembed/1.0/PROXY', '/oembed/1.0/PrOxY'];
$editor = get_users(['role' => 'administrator', 'number' => 1])[0];
wp_set_current_user($editor->ID);
add_filter('pre_http_request', $observe, PHP_INT_MAX, 3);
add_action('http_api_debug', $debug);
$defaults = [];
foreach (rest_get_server()->get_routes()['/oembed/1.0/proxy'][0]['args'] as $name => $spec) {
    if (array_key_exists('default', $spec)) {
        $defaults[$name] = $spec['default'];
    }
}
$make = static function (string $route, string $url) use ($defaults): WP_REST_Request {
    $r = new WP_REST_Request('GET', $route);
    $r->set_param('url', $url);
    $r->set_default_params($defaults);
    $r->sanitize_params();
    return $r;
};
$stale = (object) ['version' => '1.0', 'type' => 'video', 'html' => '<iframe src="https://tiers-fictif.example.invalid/B12-ANCIEN"></iframe>', 'thumbnail_url' => 'https://tiers-fictif.example.invalid/B12-ANCIEN.jpg'];
$cases = [];
$keys = [];
$removed = [];
$denied = static function (array $allcaps): array { $allcaps['edit_posts'] = false; return $allcaps; };
try {
    foreach ($routes as $i => $route) {
        foreach (['absent', 'ancien'] as $cache) {
            $phase = $i . '_' . $cache;
            $url = 'https://www.youtube.com/watch?v=B12FICTIF01&case=' . $phase;
            $request = $make($route, $url);
            $args = $request->get_params();
            unset($args['_wpnonce']);
            $key = 'oembed_' . md5(serialize($args));
            $keys[] = $key;
            delete_transient($key);
            if ($cache === 'ancien') {
                set_transient($key, $stale, 600);
                $check($phase . '_transient_reel', get_transient($key) == $stale);
                // Positive witness: the SAME native router/proxy must consume this exact cache.
                remove_filter('rest_dispatch_request', [IntegrationsCorps::class, 'apercu'], PHP_INT_MAX);
                try {
                    $witness = rest_do_request($make($route, $url));
                    $check($phase . '_temoin_cache_natif', $witness->get_status() === 200 && (array) $witness->get_data() === (array) $stale);
                } finally {
                    add_filter('rest_dispatch_request', [IntegrationsCorps::class, 'apercu'], PHP_INT_MAX, 3);
                }
            } else {
                $check($phase . '_transient_absent', get_transient($key) === false);
            }
            $start = count($events);
            $response = rest_do_request($request);
            $data = (array) $response->get_data();
            $html = $data['html'] ?? '';
            $onlyLink = $response->get_status() === 200 && ($data['type'] ?? '') === 'link'
                && array_keys($data) === ['version', 'type', 'html']
                && $html === '<a href="' . esc_url($url, ['http', 'https']) . '">' . esc_html($url) . '</a>';
            $check($phase . '_route_native', $response->get_matched_route() === '/oembed/1.0/proxy');
            $check($phase . '_lien_seul', $onlyLink);
            $check($phase . '_jamais_iframe_vignette', !isset($data['thumbnail_url']) && !preg_match('/<(iframe|img|script|video|audio)\b/i', $html));
            $check($phase . '_zero_tentative', count($events) === $start);
            $cases[] = ['route' => $route, 'cache' => $cache, 'status' => $response->get_status(), 'data' => $data, 'attempts' => count($events) - $start];
            foreach (['anonyme', 'edit_posts_revoque'] as $profile) {
                wp_set_current_user($profile === 'anonyme' ? 0 : $editor->ID);
                if ($profile === 'edit_posts_revoque') {
                    add_filter('user_has_cap', $denied, PHP_INT_MAX);
                }
                try {
                    $before = count($events);
                    $refused = rest_do_request($make($route, $url));
                    $check($phase . '_' . $profile . '_refuse', in_array($refused->get_status(), [401, 403], true) && !isset(((array) $refused->get_data())['html']) && count($events) === $before);
                } finally {
                    remove_filter('user_has_cap', $denied, PHP_INT_MAX);
                    wp_set_current_user($editor->ID);
                }
            }
            delete_transient($key);
            $check($phase . '_transient_retire', get_transient($key) === false);
            $removed[] = $key;
        }
    }
} finally {
    foreach ($keys as $key) { delete_transient($key); }
    remove_filter('pre_http_request', $observe, PHP_INT_MAX);
    remove_action('http_api_debug', $debug);
    remove_filter('user_has_cap', $denied, PHP_INT_MAX);
}
$check('transport_interdit', $transport === 0);
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'cases' => $cases, 'events' => $events, 'transport' => $transport, 'transients_removed' => $removed]);
if (in_array(false, $checks, true)) {
    throw new RuntimeException('B12_ROUTE_CASE: ' . implode(',', array_keys($checks, false, true)));
}
