<?php

declare(strict_types=1);

namespace Imagine\Demo\C22Corrections;

use Imagine\Site\Newsletters as N;
use Imagine\Site\NewslettersReglages as R;
use Imagine\Site\NewslettersRegles as Rules;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C22 requise.');
}
$case = $GLOBALS['imagine_c22_case'] ?? 'retired';
$checks = [];
$mail = $http = 0;
$fm = static function ($r) use (&$mail) { $mail++; return false; };
$fh = static function ($r) use (&$http) { $http++; return new \WP_Error('c22_interdit'); };
add_filter('pre_wp_mail', $fm, 1);
add_filter('pre_http_request', $fh, 1);
add_filter('sanitize_option_' . N::CATALOGUE, [R::class, 'nettoyerCatalogue']);
global $wpdb;
$original = get_current_user_id();
$wpdb->query('START TRANSACTION');
try {
    $main = ['id' => 'c22-correction-main', 'titre' => 'Principale fictive C22',
        'presentation' => 'Fictive.', 'principale' => true];
    $other = ['id' => 'c22-correction-autre', 'titre' => 'Ancienne fictive C22',
        'presentation' => 'Fictive.', 'principale' => false];
    $id = wp_insert_user(['user_login' => 'imagine-c22-correction',
        'user_email' => 'c22-correction@example.org', 'user_pass' => wp_generate_password(40)]);
    if (is_wp_error($id)) {
        throw new \RuntimeException('Fixture indisponible.');
    }
    wp_set_current_user($id);
    // A genuine Settings API write, including its first-add double sanitization.
    update_option(N::CATALOGUE, [$main], false);
    $checks['catalogue_temoin_non_vide'] = N::catalogue() === [$main];
    if ($case === 'retired') {
        update_option(N::CATALOGUE, [$main, $other], false);
        N::enregistrer($id, [$other['id']], N::version($id));
        $historic = N::preferences($id);
        $checks['consentement_temoin_reel'] = $historic[$other['id']]['choix'] === true
            && $historic[$other['id']]['origine'] === 'lecteur';
        update_option(N::CATALOGUE, [$main], false);
        $other['titre'] = 'Nouvelle lettre fictive interdite';
        $GLOBALS['wp_settings_errors'] = [];
        update_option(N::CATALOGUE, [$main, $other], false);
        $checks['identifiant_retire_refuse'] = N::catalogue() === [$main]
            && count(get_settings_errors(N::CATALOGUE)) > 0;
        ob_start(); N::compte(); $html = ob_get_clean();
        $checks['compte_present_sans_ancien_choix_reaffecte'] = str_contains($html, 'id="mes-newsletters"')
            && !str_contains($html, $other['titre']) && !str_contains($html, 'checked=');
        $page = N::page();
        $checks['page_presente_sans_lettre_recyclee'] = str_contains($page, $main['titre'])
            && !str_contains($page, $other['titre']);
        $checks['historique_conserve_exact'] = N::preferences($id) === $historic;
        delete_user_meta($id, N::META);
        update_option(N::CATALOGUE, [], false);
        wp_cache_flush();
        $other['principale'] = true;
        update_option(N::CATALOGUE, [$other], false);
        $checks['reserve_durable_sans_catalogue_ni_preferences'] = N::catalogue() === [];
    } elseif ($case === 'history') {
        $historic = [$other['id'] => ['choix' => true, 'date_utc' => '2026-11-25T10:00:00Z', 'origine' => 'lecteur']];
        update_user_meta($id, N::META, $historic);
        $GLOBALS['wp_settings_errors'] = [];
        update_option(N::CATALOGUE, [$main, $other], false);
        $checks['ancien_consentement_hors_catalogue_refuse'] = N::catalogue() === [$main]
            && count(get_settings_errors(N::CATALOGUE)) > 0;
        $checks['ancien_consentement_inchange'] = N::preferences($id) === $historic;
        delete_user_meta($id, N::META);
        wp_cache_flush();
        update_option(N::CATALOGUE, [$main, $other], false);
        $checks['reserve_historique_survit_effacement'] = N::catalogue() === [$main];
        $legacyId = 'c22-correction-efface-avant';
        update_user_meta($id, N::META, [$legacyId => $historic[$other['id']]]);
        delete_user_meta($id, N::META);
        wp_cache_flush();
        $other['id'] = $legacyId;
        update_option(N::CATALOGUE, [$main, $other], false);
        $checks['historique_efface_avant_edition_reste_reserve'] = N::catalogue() === [$main];
        // Ancient accepted Settings API catalogue, retired before the reserve existed.
        $other['id'] = 'c22-correction-journal-seul';
        add_option('imagine_reglages_journal_c22_legacy', ['option' => N::CATALOGUE,
            'avant' => [$main, $other], 'apres' => [$main]], '', false);
        update_option(N::CATALOGUE, [$main, $other], false);
        $checks['identifiant_historique_journal_seul_refuse'] = N::catalogue() === [$main];
    } elseif ($case === 'utf8') {
        $main['titre'] = str_repeat('é', 150);
        $main['presentation'] = str_repeat('à', 500);
        try {
            $checks['bornes_utf8_acceptees'] = Rules::catalogue([$main]) === [$main];
        } catch (\InvalidArgumentException) {
            $checks['bornes_utf8_acceptees'] = false;
        }
        foreach (['titre' => 151, 'presentation' => 501] as $key => $length) {
            $bad = $main;
            $bad[$key] = str_repeat('é', $length);
            try {
                Rules::catalogue([$bad]);
                $checks[$key . '_hors_borne_refuse'] = false;
            } catch (\InvalidArgumentException) {
                $checks[$key . '_hors_borne_refuse'] = true;
            }
        }
    } elseif ($case === 'privacy') {
        $historic = ['c22-retire-historique' => ['choix' => true,
            'date_utc' => '2026-11-25T10:00:00Z', 'origine' => 'lecteur']];
        update_user_meta($id, N::META, $historic);
        $checks['preferences_temoin_presentes'] = metadata_exists('user', $id, N::META)
            && N::preferences($id) === $historic;
        $exporters = apply_filters('wp_privacy_personal_data_exporters', []);
        $exported = [];
        for ($p = 1; $p <= 20; $p++) {
            $r = call_user_func($exporters['imagine-site']['callback'], 'c22-correction@example.org', $p);
            if (is_wp_error($r)) { throw new \RuntimeException('Export indisponible.'); }
            foreach ($r['data'] as $item) {
                foreach ($item['data'] as $field) {
                    if ($field['name'] === N::META) { $exported[] = json_decode($field['value'], true); }
                }
            }
            if ($r['done']) { break; }
        }
        $checks['export_callbacks_preferences_historiques_exactes'] = $r['done'] && $exported === [$historic];
        $erasers = apply_filters('wp_privacy_personal_data_erasers', []);
        $r = call_user_func($erasers['imagine-site']['callback'], 'c22-correction@example.org');
        wp_cache_delete($id, 'user_meta');
        $checks['effacement_callbacks_preferences_absentes'] = $r['items_removed'] && !$r['items_retained']
            && $r['done'] && !metadata_exists('user', $id, N::META);
    } else {
        throw new \RuntimeException('Cas C22 inconnu.');
    }
} finally {
    $wpdb->query('ROLLBACK');
    wp_cache_flush();
    wp_set_current_user($original);
    remove_filter('sanitize_option_' . N::CATALOGUE, [R::class, 'nettoyerCatalogue']);
    remove_filter('pre_wp_mail', $fm, 1);
    remove_filter('pre_http_request', $fh, 1);
}
$checks['aucun_mail_tente'] = $mail === 0;
$checks['aucun_HTTP_tente'] = $http === 0;
$failures = array_keys(array_filter($checks, static fn ($v) => $v !== true));
echo wp_json_encode(['case' => $case, 'checks' => $checks, 'total' => count($checks), 'failures' => $failures]);
if ($failures) { \WP_CLI::halt(1); }
