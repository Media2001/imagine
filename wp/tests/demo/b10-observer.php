<?php

declare(strict_types=1);

if (get_option('imagine_demo_site') !== 'imagine-test-demo' || wp_get_environment_type() !== 'local') {
    return;
}

// Panne native ciblée sur un seul commerce fictif de la recette, jamais un filtre global.
add_filter('pre_delete_post', static function ($delete, $post) {
    $id = (int) get_option('imagine_b10_refus_suppression', 0);
    return $id > 0 && $post->ID === $id && $post->post_type === 'imagine_vente' ? false : $delete;
}, 10, 2);

// Témoin temporaire : compter les tentatives avant le coupe-circuit local B00.
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http'] as $hook => $kind) {
    add_filter($hook, static function ($value) use ($kind) {
        $counts = get_option('imagine_b10_observations', []);
        $source = 'ambiance_';
        foreach (debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 60) as $frame) {
            if (isset($frame['file']) && basename($frame['file']) === 'PointsVente.php') {
                $source = 'b10_';
                break;
            }
        }
        $key = $source . $kind;
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        update_option('imagine_b10_observations', $counts, false);
        return $value;
    }, -1000, 1);
}
