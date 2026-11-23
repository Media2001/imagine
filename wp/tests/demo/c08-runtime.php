<?php
/** Une tranche réelle : droit Memberships/Subscriptions -> décision C-06. */
declare(strict_types=1);
namespace Imagine\Demo\C08Tests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C08 requise.');
}
$checks = [];
$fixture = get_option('imagine_c08_fixture');
$checks['adaptateur_present'] = class_exists('Imagine\\Site\\Paywall');
if ($checks['adaptateur_present']) {
    $post = get_post($fixture['article']);
    wp_set_current_user(0);
    $anon = \Imagine\Site\Paywall::decision($post);
    $checks['anonyme_extrait_connexion'] = !$anon['complet'] && $anon['bloc'] === 'connexion';
    wp_set_current_user($fixture['users']['actif']);
    $active = \Imagine\Site\Paywall::decision($post);
    $checks['actif_natif_complet'] = $active['complet'] && $active['motif'] === 'abonnement_actif';
    wp_set_current_user($fixture['users']['grace']);
    $grace = \Imagine\Site\Paywall::decision($post);
    $checks['grace_native_bandeau'] = $grace['complet'] && $grace['bloc'] === 'regularisation';
    wp_set_current_user($fixture['users']['sans-droit']);
    $checks['connecte_sans_droit_ferme'] = !\Imagine\Site\Paywall::decision($post)['complet'];
}
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
if ($failures) { \WP_CLI::halt(1); }
