<?php

declare(strict_types=1);

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
