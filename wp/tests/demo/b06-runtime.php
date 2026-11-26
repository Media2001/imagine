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
    $_POST = $savedPost;
    unset($_POST['imagine_cooperateur_oui']);
    $failAudit = static function (string $sql): string {
        return str_starts_with($sql, 'INSERT INTO') && str_contains($sql, 'imagine_reglages_journal_')
            ? 'SELECT imagine_b06_colonne_inexistante' : $sql;
    };
    $suppress = $wpdb->suppress_errors(true);
    add_filter('query', $failAudit);
    try { C::enregistrer($id); $checks['journal_en_echec_refuse'] = false; }
    catch (RuntimeException) { $checks['journal_en_echec_refuse'] = true; }
    finally { remove_filter('query', $failAudit); $wpdb->suppress_errors($suppress); }
    wp_cache_delete($id, 'user_meta');
    $checks['journal_en_echec_restaure_statut'] = get_user_meta($id, C::META, true) === $state && count(C::audits($id)) === 1;
    if ($case === 'privacy') {
        $exporters = apply_filters('wp_privacy_personal_data_exporters', []);
        $erasers = apply_filters('wp_privacy_personal_data_erasers', []);
        $checks['privacy_additive_c21'] = isset($exporters['imagine-site'], $erasers['imagine-site'], $exporters['imagine-cooperateurs'], $erasers['imagine-cooperateurs']);
        if ($checks['privacy_additive_c21']) {
        $cb = $exporters['imagine-cooperateurs']['callback'];
        $r = call_user_func($cb, 'b06-fictif@example.org', 1);
        if ($mutation === 'export_other') {
            $r['data'][0]['data'][] = ['name' => 'tiers_interdit', 'value' => $admin->user_email];
        }
        $checks['export_natif_exact'] = $r['done'] && json_decode($r['data'][0]['data'][0]['value'], true) === $state;
        $checks['export_autre_personne_absente'] = count($r['data']) === 2 && !str_contains(wp_json_encode($r), $admin->user_email);
        $failRead = static function (string $sql): string {
            return str_starts_with($sql, 'SELECT option_name,option_value FROM')
                ? 'SELECT imagine_b06_select_inexistant' : $sql;
        };
        $checks['sql_evenements_presents_avant_panne'] = count(C::audits($id)) === 1;
        $suppress = $wpdb->suppress_errors(true);
        add_filter('query', $failRead);
        try {
            try {
                $broken = call_user_func($cb, 'b06-fictif@example.org', 1);
                $checks['sql_export_jamais_complet'] = is_wp_error($broken) || ($broken['done'] ?? true) === false;
            } catch (RuntimeException) {
                $checks['sql_export_jamais_complet'] = true;
            }
            $broken = call_user_func($erasers['imagine-cooperateurs']['callback'], 'b06-fictif@example.org', 1);
            $checks['sql_effacement_incomplet_retient'] = $broken['items_retained'] === true && $broken['done'] === false && $broken['messages'] !== [];
        } finally {
            remove_filter('query', $failRead);
            $wpdb->suppress_errors($suppress);
        }
        $checks['sql_evenement_non_perdu'] = count(C::audits($id)) === 1;
        // Le premier essai peut avoir retiré l'attribut : reposer la même préimage sans nouvel audit.
        update_user_meta($id, C::META, $state);
        $reprise = call_user_func($cb, 'b06-fictif@example.org', 1);
        $checks['sql_export_reprise_complete'] = !is_wp_error($reprise) && $reprise['done'] === true && count($reprise['data']) === 2;
        if ($mutation !== 'erase_noop') { $e = call_user_func($erasers['imagine-cooperateurs']['callback'], 'b06-fictif@example.org', 1); }
        else { $e = ['items_removed' => true, 'items_retained' => false, 'done' => true]; }
        wp_cache_delete($id, 'user_meta');
        $checks['effacement_natif_attribut_absent'] = $e['items_removed'] && $e['done'] && !metadata_exists('user', $id, C::META);
        $checks['audit_cible_anonymise'] = C::audits($id) === [];
        // Plus d'un lot : la relecture finale échoue avec un événement encore présent.
        if ($mutation !== 'erase_noop') {
            foreach (range(1, 51) as $n) {
                add_option('imagine_reglages_journal_b06reprise' . $id . '_' . $n, [
                    'option'=>C::META . '_' . $id, 'avant'=>$state, 'apres'=>$state,
                    'quand_utc'=>$state['date_utc'], 'qui_id'=>$admin->ID, 'qui_login'=>$admin->user_login,
                ], '', false);
            }
            $checks['sql_relecture_51_evenements_presents'] = count(C::audits($id)) === 51;
            $reads = 0;
            $failSecond = static function (string $sql) use (&$reads): string {
                if (str_starts_with($sql, 'SELECT option_name,option_value FROM') && ++$reads === 2) {
                    return 'SELECT imagine_b06_relecture_inexistante';
                }
                return $sql;
            };
            $suppress = $wpdb->suppress_errors(true);
            add_filter('query', $failSecond);
            try { $partial = C::effacer('b06-fictif@example.org'); }
            finally { remove_filter('query', $failSecond); $wpdb->suppress_errors($suppress); }
            $checks['sql_relecture_finale_incomplete'] = $reads === 2 && $partial['items_removed'] && $partial['items_retained'] && !$partial['done'];
            $checks['sql_relecture_evenement_restant'] = count(C::audits($id)) === 1;
            $retry = C::effacer('b06-fictif@example.org');
            $checks['sql_effacement_reprise_complete'] = $retry['items_removed'] && !$retry['items_retained'] && $retry['done'] && C::audits($id) === [];
        }
        }
    } else {
        $_POST = $savedPost; unset($_POST['imagine_cooperateur_oui']);
        C::enregistrer($id);
        $off = get_user_meta($id, C::META, true);
        $checks['retrait_audite'] = $off['cooperateur'] === false && count(C::audits($id)) === 2;
        wp_set_current_user($id);
        $checks['retrait_referme'] = !C::autorise();
        ob_start(); C::compte(); $offAccount = ob_get_clean();
        if ($mutation === 'display') { $offAccount .= 'Source : administration<time>' . $off['date_utc'] . '</time>'; }
        $checks['compte_retrait_sans_source_date'] = str_contains($offAccount, 'Coopérateur : non') && !str_contains($offAccount, 'administration') && !str_contains($offAccount, '<time>');
        wp_set_current_user($admin->ID);
        ob_start(); C::fiche(get_userdata($id)); $offForm = ob_get_clean();
        if ($mutation === 'display') { $offForm .= 'Source : administration<time>' . $off['date_utc'] . '</time>'; }
        $checks['fiche_retrait_sans_source_date'] = str_contains($offForm, 'imagine_cooperateur_oui') && !str_contains($offForm, 'Source : administration') && !str_contains($offForm, '<time>');
    }
    if ($mutation === 'listener') { add_action(C::ACCROCHE, '__return_null'); }
    $checks['accroche_nommee_sans_ecouteur'] = C::ACCROCHE === 'imagine_cooperateur_modifie' && has_action(C::ACCROCHE) === false;
    if ($mutation === 'mail') { wp_mail('b06-fictif@example.org', 'FICTIF B06', 'FICTIF'); }
    if ($mutation === 'http') { wp_remote_get('https://example.org/b06-fictif'); }
} finally {
    $wpdb->query('ROLLBACK'); wp_cache_flush(); wp_set_current_user($original);
    remove_filter('pre_wp_mail', $fm, 1); remove_filter('pre_http_request', $fh, 1);
}
$checks['aucun_mail_tente'] = $mail === 0;
$checks['aucun_http_tente'] = $http === 0;
$failures = array_keys(array_filter($checks, static fn ($v) => $v !== true));
echo wp_json_encode(['case' => $case, 'mutation' => $mutation, 'checks' => $checks, 'total' => count($checks), 'failures' => $failures]);
if ($failures) { WP_CLI::halt(1); }
