<?php

declare(strict_types=1);

// Mutation témoin active, distincte de l'observateur passif ; temporaire, fictif seul.
if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || ($_SERVER['HTTP_X_IMAGINE_B11_MUTATION'] ?? '') !== 'no-persist') {
    return;
}
add_filter('update_post_metadata', static function ($value, $id, $key) {
    $f = get_option('imagine_b11_fixture', []);
    if (in_array((int) $id, [(int) ($f['issue'] ?? 0), (int) ($f['article'] ?? 0)], true)
        && in_array($key, ['_imagine_video', '_imagine_podcast'], true)) {
        return true; // Simule une écriture annoncée réussie, mais ignorée réellement.
    }
    return $value;
}, PHP_INT_MAX, 3);
