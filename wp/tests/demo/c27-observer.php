<?php

declare(strict_types=1);

// Accès de prévisualisation limité aux requêtes de la recette fictive ; aucun réglage Woo modifié.
if (wp_get_environment_type() === 'local' && get_option('imagine_demo_site') === 'imagine-test-demo'
    && ($_SERVER['HTTP_X_IMAGINE_C27_RECETTE'] ?? '') === 'recette-fictive') {
    add_filter('woocommerce_coming_soon_exclude', '__return_true');
}

// Instrumentation temporaire ; le coupe-circuit B00 reste inchangé.
if (wp_get_environment_type() === 'local' && get_option('imagine_demo_site') === 'imagine-test-demo'
    && ($_SERVER['HTTP_X_IMAGINE_C27_SETTINGS'] ?? '') === 'recette-fictive') {
    add_filter('allowed_options', static function (array $items): array {
        $items['imagine_reglages'] = ['imagine_acquisition_choix'];
        return $items;
    }, PHP_INT_MAX);
    if (($_SERVER['HTTP_X_IMAGINE_C27_FAILURE'] ?? '') === 'journal') {
        $GLOBALS['wpdb']->suppress_errors(true);
        add_filter('query', static function (string $query): string {
            if (str_contains($query, 'INSERT INTO') && str_contains($query, 'imagine_reglages_journal_')) {
                return 'INSERT INTO imagine_c27_table_absente VALUES (1)';
            }
            return $query;
        });
    }
}
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http'] as $hook => $kind) {
    add_filter($hook, static function ($value) use ($kind) {
        $counts = get_option('imagine_c27_observations', []);
        $source = 'ambiance_';
        foreach (debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 40) as $frame) {
            if (isset($frame['file']) && str_starts_with(basename($frame['file']), 'Acquisition')) {
                $source = 'c27_';
                break;
            }
        }
        $key = $source . $kind;
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        update_option('imagine_c27_observations', $counts, false);
        return $value;
    }, -1000, 1);
}
