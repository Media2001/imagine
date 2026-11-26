<?php

declare(strict_types=1);

namespace Imagine\Demo\C22;

use Imagine\Site\Newsletters as N;
use Imagine\Site\NewslettersReglages as R;
use Imagine\Site\Confidentialite as P;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C22 requise.');
}
$checks = ['raccord_present' => class_exists(N::class)];
$mail = $http = 0;
$fm = static function ($r) use (&$mail) { $mail++; return false; };
$fh = static function ($r) use (&$http) { $http++; return new \WP_Error('c22_interdit'); };
add_filter('pre_wp_mail', $fm, 1);
add_filter('pre_http_request', $fh, 1);
if ($checks['raccord_present']) {
    global $wpdb;
    $original = get_current_user_id();
    $wpdb->query('START TRANSACTION');
    try {
        $catalogue = [
            ['id' => 'main', 'titre' => 'Principale fictive', 'presentation' => 'Fictive.', 'principale' => true],
            ['id' => 'autre', 'titre' => 'Autre fictive', 'presentation' => 'Fictive.', 'principale' => false],
        ];
        update_option(N::CATALOGUE, $catalogue, false);
        delete_option(N::CREATION);
        $u = get_user_by('login', 'a-papier');
        $other = get_user_by('login', 'a-sepa4');
        wp_set_current_user($u->ID);
        delete_user_meta($u->ID, N::META);
        $checks['defaut_non_choisi'] = N::preferences($u->ID) === [];
        $version = N::version($u->ID);
        N::enregistrer($u->ID, ['main'], $version);
        $on = get_user_meta($u->ID, N::META, true);
        $checks['choix_date_lecteur'] = $on['main']['choix'] === true
            && $on['autre']['choix'] === false && $on['main']['origine'] === 'lecteur'
            && (bool) preg_match('/^\d{4}-\d{2}-\d{2}T/', $on['main']['date_utc']);
        $beforeOther = get_user_meta($other->ID, N::META, true);
        try {
            N::enregistrer($other->ID, [], N::version($other->ID));
            $checks['autre_compte_refuse'] = false;
        } catch (\RuntimeException) {
            $checks['autre_compte_refuse'] = get_user_meta($other->ID, N::META, true) === $beforeOther;
        }
        try {
            N::enregistrer($u->ID, [], $version);
            $checks['version_perimee_refusee'] = false;
        } catch (\RuntimeException) {
            $checks['version_perimee_refusee'] = get_user_meta($u->ID, N::META, true) === $on;
        }
        N::enregistrer($u->ID, [], N::version($u->ID));
        $checks['decocher'] = N::preferences($u->ID)['main']['choix'] === false;
        $exporters = apply_filters('wp_privacy_personal_data_exporters', []);
        $exp = call_user_func($exporters['imagine-site']['callback'], $u->user_email);
        $checks['export_natif_preferences'] = !is_wp_error($exp)
            && str_contains(wp_json_encode($exp), N::META) && str_contains(wp_json_encode($exp), 'date_utc');
        $erasers = apply_filters('wp_privacy_personal_data_erasers', []);
        $erase = call_user_func($erasers['imagine-site']['callback'], $u->user_email);
        $checks['effacement_natif_preferences'] = !$erase['items_retained'] && !metadata_exists('user', $u->ID, N::META);
        foreach (['non', 'oui'] as $mode) {
            update_option(N::CREATION, $mode, false);
            $id = wp_insert_user(['user_login' => 'imagine-c22-' . $mode, 'user_email' => 'c22-' . $mode . '@example.org',
                'user_pass' => wp_generate_password(40)]);
            if (is_wp_error($id)) {
                throw new \RuntimeException('Fixture indisponible.');
            }
            $prefs = N::preferences($id);
            $checks['creation_' . $mode] = $mode === 'non' ? $prefs === [] :
                ($prefs['main']['choix'] === true && $prefs['main']['origine'] === 'defaut_creation');
        }
        $id = wp_insert_user(['user_login' => 'imagine-c22-sans', 'user_email' => 'c22@sans-email.imagine.invalid',
            'user_pass' => wp_generate_password(40), 'meta_input' => ['imagine_sans_email' => '1']]);
        $checks['creation_sans_email_fermee'] = !is_wp_error($id) && N::preferences($id) === [];
        wp_set_current_user(get_user_by('login', 'a-sansmail')->ID);
        ob_start(); N::compte(); $html = ob_get_clean();
        $checks['sans_email_phrase_pas_cases'] = !str_contains($html, 'type="checkbox"') && str_contains($html, 'sans email');
        wp_set_current_user($u->ID);
        $catalogue[] = ['id' => 'quatrieme', 'titre' => 'Quatrième fictive', 'presentation' => 'Fictive.', 'principale' => false];
        update_option(N::CATALOGUE, $catalogue, false);
        ob_start(); N::compte(); $html = ob_get_clean();
        $checks['quatrieme_compte_page'] = str_contains($html, 'Quatrième fictive') && str_contains(N::page(), 'Quatrième fictive');
        wp_set_current_user(0);
        $html = N::page();
        $checks['anonyme_emplacement_pas_formulaire'] = str_contains($html, 'imagine-newsletters-inscription-brevo') && !str_contains($html, '<form');
        $checks['sanitize_creation_ferme'] = R::nettoyerCreation('invalide') === 'non';
        $checks['sanitize_catalogue_invalide_conserve'] = R::nettoyerCatalogue('invalide') === $catalogue;
    } finally {
        $wpdb->query('ROLLBACK');
        wp_cache_flush();
        wp_set_current_user($original);
    }
}
remove_filter('pre_wp_mail', $fm, 1);
remove_filter('pre_http_request', $fh, 1);
$checks['aucun_mail_tente'] = $mail === 0;
$checks['aucun_HTTP_tente'] = $http === 0;
$failures = array_keys(array_filter($checks, static fn ($v) => $v !== true));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures]);
if ($failures) { \WP_CLI::halt(1); }
