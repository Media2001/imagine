<?php

declare(strict_types=1);

// Observateur temporaire fictif, en amont du coupe-circuit B00 inchangé.
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http'] as $hook => $kind) {
    add_filter($hook, static function ($value) use ($kind) {
        $counts = get_option('imagine_b09_observations', []);
        $source = 'ambiance_';
        foreach (debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 40) as $frame) {
            if (isset($frame['file']) && in_array(basename($frame['file']), ['Contact.php', 'ContactConfidentialite.php', 'AutresPages.php'], true)) {
                $source = 'b09_';
                break;
            }
        }
        $key = $source . $kind;
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        update_option('imagine_b09_observations', $counts, false);
        return $value;
    }, -1000, 1);
}
