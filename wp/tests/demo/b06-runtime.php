<?php

declare(strict_types=1);

use Imagine\Site\Cooperateurs as C;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new RuntimeException('Démo fictive seule.');
}
if (!class_exists(C::class)) {
    echo wp_json_encode(['failures' => ['ecran_attribut_natif_absent'], 'total' => 1]);
    WP_CLI::halt(1);
}
$checks = [];
$case = $GLOBALS['imagine_b06_case'] ?? 'attribute';
$mutation = $GLOBALS['imagine_b06_mutation'] ?? '';
global $wpdb;
$original = get_current_user_id();
$mail = $http = 0;
$fm = static function ($r) use (&$mail) { $mail++; return false; };
$fh = static function ($r) use (&$http) { $http++; return new WP_Error('b06_interdit'); };
add_filter('pre_wp_mail', $fm, 1);
add_filter('pre_http_request', $fh, 1);
$wpdb->query('START TRANSACTION');
try {
    $id = wp_insert_user(['user_login' => 'imagine-b06-fictif', 'user_email' => 'b06-fictif@example.org',
        'user_pass' => wp_generate_password(40), 'role' => 'subscriber']);
    if (is_wp_error($id)) { throw new RuntimeException('Fixture absente.'); }
    $admin = get_user_by('login', 'admin');
    $checks['fixture_reelle'] = $id > 0 && $admin && in_array('administrator', $admin->roles, true);
    wp_set_current_user($admin->ID);
    ob_start(); do_action('edit_user_profile', get_userdata($id)); $html = ob_get_clean();
    $checks['fiche_native_nonce'] = str_contains($html, 'name="imagine_cooperateur_nonce"') && str_contains($html, 'imagine_cooperateur_oui');
    $_SERVER['REQUEST_METHOD'] = 'POST';
    $_POST = ['imagine_cooperateur_present' => '1', 'imagine_cooperateur_nonce' => wp_create_nonce('imagine_cooperateur_' . $id), 'imagine_cooperateur_oui' => '1'];
    do_action('edit_user_profile_update', $id);
    $state = get_user_meta($id, C::META, true);
    $checks['attribut_source_date'] = ($state['cooperateur'] ?? null) === true && $state['source'] === 'administration'
        && preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/D', $state['date_utc']) === 1;
    $audit = C::audits($id);
    $checks['audit_ajout'] = count($audit) === 1 && reset($audit)['qui_id'] === $admin->ID
        && reset($audit)['apres'] === $state && reset($audit)['quand_utc'] === $state['date_utc'];
    do_action('edit_user_profile_update', $id);
    $checks['sans_faux_changement'] = count(C::audits($id)) === 1;
    wp_set_current_user($id);
    $checks['coop_lit'] = C::autorise();
    ob_start(); do_action('woocommerce_account_dashboard'); $account = ob_get_clean();
    $checks['compte_natif_statut_source'] = str_contains($account, 'id="mon-statut-cooperateur"')
        && str_contains($account, 'administration') && str_contains($account, 'Coopérateur : oui');
    $savedPost = $_POST;
    $_POST['imagine_cooperateur_oui'] = '0';
    try { C::enregistrer($id); $checks['auto_refus'] = false; } catch (RuntimeException) { $checks['auto_refus'] = true; }
    wp_set_current_user($admin->ID);
    $_POST = $savedPost; $_POST['imagine_cooperateur_nonce'] = 'faux';
    try { C::enregistrer($id); $checks['nonce_refus'] = false; } catch (RuntimeException) { $checks['nonce_refus'] = true; }
    $checks['refus_sans_effet'] = get_user_meta($id, C::META, true) === $state && count(C::audits($id)) === 1;
    if ($case === 'privacy') {
        $exporters = apply_filters('wp_privacy_personal_data_exporters', []);
        $erasers = apply_filters('wp_privacy_personal_data_erasers', []);
        $checks['privacy_additive_c21'] = isset($exporters['imagine-site'], $erasers['imagine-site'], $exporters['imagine-cooperateurs'], $erasers['imagine-cooperateurs']);
        $cb = $exporters['imagine-cooperateurs']['callback'];
        $r = call_user_func($cb, 'b06-fictif@example.org', 1);
        $checks['export_natif_exact'] = $r['done'] && json_decode($r['data'][0]['data'][0]['value'], true) === $state;
        $checks['export_autre_personne_absente'] = count($r['data']) === 2 && !str_contains(wp_json_encode($r), $admin->user_email);
        if ($mutation !== 'erase_noop') { $e = call_user_func($erasers['imagine-cooperateurs']['callback'], 'b06-fictif@example.org', 1); }
        else { $e = ['items_removed' => true, 'items_retained' => false, 'done' => true]; }
        wp_cache_delete($id, 'user_meta');
        $checks['effacement_natif_attribut_absent'] = $e['items_removed'] && $e['done'] && !metadata_exists('user', $id, C::META);
        $checks['audit_cible_anonymise'] = C::audits($id) === [];
    } else {
        $_POST = $savedPost; unset($_POST['imagine_cooperateur_oui']);
        C::enregistrer($id);
        $off = get_user_meta($id, C::META, true);
        $checks['retrait_audite'] = $off['cooperateur'] === false && count(C::audits($id)) === 2;
        wp_set_current_user($id);
        $checks['retrait_referme'] = !C::autorise();
    }
} finally {
    $wpdb->query('ROLLBACK'); wp_cache_flush(); wp_set_current_user($original);
    remove_filter('pre_wp_mail', $fm, 1); remove_filter('pre_http_request', $fh, 1);
}
$checks['aucun_mail_tente'] = $mail === 0;
$checks['aucun_http_tente'] = $http === 0;
$failures = array_keys(array_filter($checks, static fn ($v) => $v !== true));
echo wp_json_encode(['case' => $case, 'mutation' => $mutation, 'checks' => $checks, 'total' => count($checks), 'failures' => $failures]);
if ($failures) { WP_CLI::halt(1); }
