<?php

declare(strict_types=1);

// Instrumentation bornée au seul formulaire C25 de cette recette fictive.
if (wp_get_environment_type() === 'local' && get_option('imagine_demo_site') === 'imagine-test-demo'
    && ($_SERVER['HTTP_X_IMAGINE_C25_SETTINGS'] ?? '') === 'recette-fictive') {
    add_filter('allowed_options', static function (array $options): array {
        $options['imagine_reglages'] = ['imagine_retractation_reglages'];
        return $options;
    }, PHP_INT_MAX);
    if (($_SERVER['HTTP_X_IMAGINE_C25_FAILURE'] ?? '') === 'journal') {
        $GLOBALS['wpdb']->suppress_errors(true);
        add_filter('query', static function (string $query): string {
            if (str_contains($query, 'INSERT INTO') && str_contains($query, 'imagine_reglages_journal_')) {
                $counts = get_option('imagine_c25_observations', []);
                $counts['settings_SQL_refus'] = ($counts['settings_SQL_refus'] ?? 0) + 1;
                update_option('imagine_c25_observations', $counts, false);
                return 'INSERT INTO imagine_c25_table_inexistante VALUES (1)';
            }
            return $query;
        });
    }
}

// Observateur de recette fictive, retiré après la recette. Le coupe-circuit B00 reste actif.
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http', 'woocommerce_order_status_changed' => 'statut',
    'woocommerce_subscription_status_updated' => 'abonnement', 'woocommerce_order_refunded' => 'remboursement'] as $hook => $kind) {
    $fn = static function ($value = null) use ($kind) {
        $counts = get_option('imagine_c25_observations', []);
        $source = 'ambiance_';
        foreach (debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 40) as $frame) {
            if (isset($frame['file']) && in_array(basename($frame['file']), ['Retractation.php', 'RetractationConfidentialite.php', 'RetractationReglages.php'], true)) {
                $source = 'c25_';
                break;
            }
        }
        $key = $source . $kind;
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        update_option('imagine_c25_observations', $counts, false);
        return $value;
    };
    add_filter($hook, $fn, -1000, 1);
}
