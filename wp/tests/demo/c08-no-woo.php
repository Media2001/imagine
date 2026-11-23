<?php
/** Processus WP isolé --skip-plugins --skip-themes : aucune désactivation persistante. */
declare(strict_types=1);
namespace Imagine\Demo\C08NoWoo;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C08 requise.');
}
$checks = ['woocommerce_reellement_absent' => !function_exists('wc_get_page_permalink')];
$args = ['complet' => false];
try {
    ob_start();
    require WP_CONTENT_DIR . '/themes/imagine/parts/paywall-regularisation.php';
    $html = ob_get_clean();
    $checks['bloc_sans_woo_sans_exception'] = true;
    $checks['bloc_sans_woo_lien_connexion'] = str_contains($html, esc_url(wp_login_url()));
    $checks['bloc_sans_woo_pas_promesse_lecture'] = !str_contains($html, 'la lecture reste disponible');
} catch (\Throwable $e) {
    if (ob_get_level()) { ob_end_clean(); }
    $checks['bloc_sans_woo_sans_exception'] = false;
}
require_once WP_CONTENT_DIR . '/themes/imagine/functions.php';
$f = get_option('imagine_c08_fixture');
$GLOBALS['post'] = get_post($f['article']);
setup_postdata($GLOBALS['post']);
ob_start();
\Imagine\Theme\imagine_article_body();
$withoutAdapter = ob_get_clean();
$checks['corps_sans_adaptateur_ferme_sans_password'] = !str_contains($withoutAdapter, 'Les lucioles violettes de C08 gardent le secret du village fictif.');
$checks['corps_sans_adaptateur_extrait_public'] = str_contains($withoutAdapter, 'Extrait public C08');
require_once WP_CONTENT_DIR . '/plugins/imagine-site/Paywall.php';
$f = get_option('imagine_c08_fixture');
wp_set_current_user($f['users']['actif']);
$checks['droits_sans_woo_fermes'] = !\Imagine\Site\Paywall::decision(get_post($f['article']))['complet'];
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures]);
if ($failures) { \WP_CLI::halt(1); }
