<?php
/** C09 : refus réels sur lectures injectées, aucune mutation ni appel à une autre cible. */
declare(strict_types=1);
namespace Imagine\Demo\C09Safety;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new \RuntimeException('Recette refusée.'); }
$checks = [];
$seed = WP_CONTENT_DIR . '/imagine-demo-build/c09-seed.php';
$denied = static function (string $expected) use ($seed): bool {
    try { ob_start(); require $seed; ob_end_clean(); return false; }
    catch (\Throwable $error) { if (ob_get_level()) { ob_end_clean(); } return str_contains($error->getMessage(), $expected); }
};
$wrongSite = static fn () => 'imagine-test-autre';
add_filter('pre_option_imagine_demo_site', $wrongSite);
$checks['mauvais_nom_refuse'] = $denied('C09 refuse cette cible');
remove_filter('pre_option_imagine_demo_site', $wrongSite);
$wrongHome = static fn () => 'http://autre-site.invalid';
$sentinel = static function () { throw new \RuntimeException('APRES_GARDE_AVANT_ECRITURE'); };
add_filter('pre_option_home', $wrongHome);
// Sentinelle avant toute écriture si la garde URL manquait : pas de reseed de test.
add_filter('pre_wp_mail', $sentinel, 0);
$checks['mauvaise_url_refusee_avant_toute_action'] = $denied('C09 refuse cette cible');
remove_filter('pre_option_home', $wrongHome);
remove_filter('pre_wp_mail', $sentinel, 0);
$allowMail = static fn () => true;
add_filter('pre_wp_mail', $allowMail, PHP_INT_MAX);
$checks['mail_non_coupe_refuse_sans_envoyer'] = $denied('Garde hors ligne C09 absente');
remove_filter('pre_wp_mail', $allowMail, PHP_INT_MAX);
$fixture = get_option('imagine_c09_fixture');
$id = $fixture['users']['V-DEC'];
$foreignUser = static function ($value, $userId, $key) use ($id) {
    return $userId === $id && $key === '_imagine_c09_fixture' ? ['autre-proprietaire'] : $value;
};
add_filter('get_user_metadata', $foreignUser, 10, 3);
$checks['compte_non_possede_refuse'] = $denied('Collision de compte C09');
remove_filter('get_user_metadata', $foreignUser, 10);
$memberId = $fixture['memberships']['A-CARTE'];
$foreignMember = static function ($value, $postId, $key) use ($memberId) {
    return $postId === $memberId && $key === '_imagine_c09_fixture' ? ['autre-proprietaire'] : $value;
};
add_filter('get_post_metadata', $foreignMember, 10, 3);
$checks['adhesion_non_possedee_refusee'] = $denied('Adhésion étrangère sur profil C09');
remove_filter('get_post_metadata', $foreignMember, 10);
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
if ($failures) { \WP_CLI::halt(1); }
