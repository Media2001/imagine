<?php

declare(strict_types=1);

// Témoin temporaire uniquement sur le site fictif ; le coupe-circuit B00 reste intact.
if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    return;
}
if (($_SERVER['HTTP_X_IMAGINE_B11_SETTINGS'] ?? '') === 'fictif') {
    add_filter('use_block_editor_for_post', static function (bool $use, $post): bool {
        $f = get_option('imagine_b11_fixture', []);
        return in_array($post->ID, [$f['issue'] ?? 0, $f['article'] ?? 0], true) ? false : $use;
    }, PHP_INT_MAX, 2);
    add_filter('allowed_options', static function (array $items): array {
        $items['imagine_reglages'] = ['imagine_medias'];
        return $items;
    }, PHP_INT_MAX);
}
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http', 'pre_oembed_result' => 'oembed'] as $hook => $kind) {
    add_filter($hook, static function ($value) use ($kind) {
        $phase = $_GET['b11_observe'] ?? 'ambiance';
        if (!is_string($phase) || !preg_match('/\A[a-z0-9-]+\z/D', $phase)) {
            $phase = 'ambiance';
        }
        $counts = get_option('imagine_b11_observations', []);
        $key = $phase . '_' . $kind;
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        update_option('imagine_b11_observations', $counts, false);
        return $value;
    }, -1000, 1);
}
