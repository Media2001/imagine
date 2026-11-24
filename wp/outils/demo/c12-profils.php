<?php
/** Complément du script C09 : seuls V-DEC/V-DEC-FIN, indicateur email explicitement fictif. */
declare(strict_types=1);
namespace Imagine\Demo\C12;

function profil(int $id, string $code, bool $reset = false): void
{
    if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
        || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085'
        || !in_array($code, ['V-DEC', 'V-DEC-FIN'], true)
        || get_user_meta($id, '_imagine_c09_fixture', true) !== $code
        || get_userdata($id)->user_login !== strtolower($code)) {
        throw new \RuntimeException('Profil C12 refusé.');
    }
    if (!get_option('imagine_c12_fixture')) {
        // Isoler les variables du seed ; ne pas écraser l'ID du compte appelant.
        (static function (): void { ob_start(); require __DIR__ . '/c12-seed.php'; ob_end_clean(); })();
    }
    update_user_meta($id, 'imagine_email_confirme', '1');
    $key = \Imagine\Site\Decouverte::key($id);
    if ($reset) {
        delete_option($key); // Seulement le reset explicite des deux personnages fictifs.
    }
    if ($code === 'V-DEC-FIN' && get_option($key, null) === null) {
        $settings = \Imagine\Site\Decouverte::defauts();
        $settings['ouverture'] = 'premiere_lecture';
        $settings['numeros'] = [(string) get_option('imagine_demo_manifest')['demo-2026-t4']];
        $articles = array_values(get_option('imagine_c12_fixture'));
        add_option($key, ['debut' => gmdate('Y-m-d H:i:s', time() - DAY_IN_SECONDS),
            'reglages' => $settings, 'articles' => array_slice($articles, 0, $settings['nombre'])], '', false);
    }
}
