<?php

/** B05 native, transactional probes; no fictional profile is reset. */

declare(strict_types=1);

namespace Imagine\Demo\B05;

if (
    !defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
) {
    throw new \RuntimeException('Cible fictive B05 requise.');
}
$checks = ['raccord_present' => class_exists('Imagine\\Site\\Partenaires')];
if ($checks['raccord_present']) {
    global $wpdb;
    $manifest = get_option('imagine_demo_manifest');
    $one = (int) $manifest['demo-partners-1'];
    $two = (int) $manifest['demo-partners-2'];
    $option = \Imagine\Site\Partenaires::OPTION;
    $user = get_current_user_id();
    $wpdb->query('START TRANSACTION');
    try {
        wp_set_current_user(get_user_by('login', 'e-admin')->ID);
        // Invoke the actual B05 admin-init closure only: WP-CLI is not wp-admin,
        // Woo's unrelated admin-init requires its normal HTTP bootstrap.
        global $wp_filter;
        foreach ($wp_filter['admin_init']->callbacks as $callbacks) {
            foreach ($callbacks as $callback) {
                $fn = $callback['function'];
                if (
                    $fn instanceof \Closure
                    && (new \ReflectionFunction($fn))->getFileName() === WP_PLUGIN_DIR . '/imagine-site/Partenaires.php'
                ) {
                    $fn();
                }
            }
        }
        $setting = get_registered_settings()[$option] ?? [];
        $checks['settings_API_C10'] = ($setting['group'] ?? '') === 'imagine_reglages'
            && ($setting['show_in_rest'] ?? null) === false;
        delete_option($option);
        $checks['defaut_sans_selection'] = \Imagine\Site\Partenaires::selection() === null;
        update_option($option, (string) $one, false);
        $checks['choix_publie'] = \Imagine\Site\Partenaires::selection()?->ID === $one;
        update_option($option, (string) $two, false);
        $checks['un_seul_choix_remplace'] = \Imagine\Site\Partenaires::selection()?->ID === $two;
        foreach (['-1', [$one, $two], '12abc', (string) $manifest['demo-2026-t1-ouvert'], '999999999'] as $i => $invalid) {
            $checks['invalide_conserve_' . $i] = \Imagine\Site\Partenaires::nettoyer($invalid) === $two;
        }
        $checks['formulaire_ancien_conserve'] = \Imagine\Site\Partenaires::nettoyer(null) === $two;
        $checks['effacement_explicite'] = \Imagine\Site\Partenaires::nettoyer('0') === 0;
        $wpdb->update($wpdb->posts, ['post_status' => 'draft'], ['ID' => $two]);
        clean_post_cache($two);
        $checks['depublie_ferme'] = \Imagine\Site\Partenaires::selection() === null;
        $checks['depublie_refuse'] = \Imagine\Site\Partenaires::nettoyer((string) $two) === 0;
        $wpdb->update($wpdb->posts, ['post_status' => 'publish'], ['ID' => $two]);
        clean_post_cache($two);
        ob_start();
        \Imagine\Site\Partenaires::champ();
        $html = ob_get_clean();
        $checks['champ_label_aucun_deux_choix'] = str_contains($html, 'Partenaire du mois')
            && str_contains($html, 'value="0"') && str_contains($html, 'value="' . $one . '"')
            && str_contains($html, 'value="' . $two . '"') && !str_contains($html, 'multiple');
    } finally {
        $wpdb->query('ROLLBACK');
        wp_cache_flush();
        wp_set_current_user($user);
    }
}
$failures = array_keys(array_filter($checks, static fn ($v) => $v !== true));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures], JSON_UNESCAPED_UNICODE);
if ($failures) {
    \WP_CLI::halt(1);
}
