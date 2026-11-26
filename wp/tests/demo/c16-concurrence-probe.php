<?php
/** Test-only barrier/fault injection; installed temporarily on imagine-test-demo. */
declare(strict_types=1);

add_action('plugins_loaded', static function (): void {
    if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
        || home_url() !== 'http://192.168.129.32:8085' || ($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST'
        || ($_GET['page'] ?? '') !== 'imagine-commandes' || ($_POST['c16_action'] ?? '') !== 'creer') {
        return;
    }
    $config = get_option('imagine_c16_recette_v2');
    if (!is_array($config) || ($config['token'] ?? '') !== ($_POST['token'] ?? '')
        || ($config['uid'] ?? 0) !== get_current_user_id() || !current_user_can('imagine_creer_compte_client')) {
        return;
    }
    $directory = WP_CONTENT_DIR . '/imagine-demo-build/c16-recette-v2';
    if ($config['mode'] === 'concurrence') {
        add_filter('query', static function (string $query) use ($directory): string {
            if (!str_contains($query, 'SELECT GET_LOCK(') || !str_contains($query, "'imagine_c16_")
                || str_contains($query, 'imagine_c16_email_')) {
                return $query;
            }
            global $wpdb;
            $connection = (int) $wpdb->get_var('SELECT CONNECTION_ID()');
            file_put_contents($directory . '/arrive-' . $connection, (string) microtime(true), LOCK_EX);
            $deadline = microtime(true) + 10;
            do {
                $arrivals = glob($directory . '/arrive-*');
                if (count($arrivals) === 2) {
                    return $query;
                }
                usleep(10000);
            } while (microtime(true) < $deadline);
            throw new RuntimeException('C16 barrier: two distinct requests required before GET_LOCK.');
        });
    } elseif ($config['mode'] === 'interruption') {
        $key = 'imagine_c16_brouillon_' . $config['uid'] . '_' . $config['token'];
        add_action('set_transient_' . $key, static function ($value) use ($directory): void {
            if (!empty($value['commence']) && !isset($value['resultat'])) {
                file_put_contents($directory . '/interruption', 'commence persisted', LOCK_EX);
                throw new RuntimeException('C16 deliberate interruption after persisted commence.');
            }
        });
    }
});
