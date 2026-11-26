<?php

declare(strict_types=1);

// Observateur fictif retiré après la recette ; le coupe-circuit B00 reste en place.
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http'] as $hook => $kind) {
    add_filter($hook, static function ($value) use ($kind) {
        $counts = get_option('imagine_b08_observations', []);
        $source = 'ambiance_';
        foreach (debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 40) as $frame) {
            if (isset($frame['file']) && in_array(basename($frame['file']), ['Sujet.php', 'SujetConfidentialite.php', 'Soutenir.php', 'Cooperative.php'], true)) {
                $source = 'b08_';
                break;
            }
        }
        $key = $source . $kind;
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        update_option('imagine_b08_observations', $counts, false);
        return $value;
    }, -1000, 1);
}
