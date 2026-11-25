<?php
/** C13 : premier tracer — calendrier et permissions réels. */
declare(strict_types=1);
namespace Imagine\Demo\C13Tests;
$checks = [];
$checks['raccord_present'] = class_exists(\Imagine\Site\EnvoiNatif::class)
    && class_exists(\Imagine\Site\ListeEnvoiAdmin::class);
if ($checks['raccord_present']) {
    $checks['calendrier_15_clotures'] = count(\Imagine\Site\EnvoiNatif::calendrier()->numeros) === 15;
    $fixture = get_option('imagine_c09_fixture');
    foreach (['E-ABO' => true, 'E-ADMIN' => true, 'E-REDAC' => false, 'A-CARTE' => false] as $profile => $allowed) {
        wp_set_current_user($fixture['users'][$profile]);
        $checks['capacite_' . $profile] = \Imagine\Site\ListeEnvoiAdmin::autorise() === $allowed;
    }
    $checks['raccord_natif_et_C07'] = method_exists(\Imagine\Site\EnvoiNatif::class, 'apercu');
    if ($checks['raccord_natif_et_C07']) {
        $view = \Imagine\Site\EnvoiNatif::apercu('DEMO-2027-T1');
        $excluded = array_column($view['exclus'], 'motif', 'abonnement_id');
        $checks['C09_exclus_motifs'] = ($excluded[(string) $fixture['subscriptions']['A-SUSP']] ?? '') === 'suspendu'
            && ($excluded[(string) $fixture['subscriptions']['A-VIR']] ?? '') === 'virement_non_valide'
            && ($excluded[(string) $fixture['subscriptions']['A-EXPIRE']] ?? '') === 'expire';
        $included = array_column($view['liste']->lignes, 'abonnement_id');
        $checks['paiement_fictif_C09_A_SANSMAIL_inclus'] = in_array((string) $fixture['subscriptions']['A-SANSMAIL'], $included, true);
        $checks['repartition_exacte'] = $view['belgique'] + $view['etranger'] === count($view['liste']->lignes);
        $checks['positif_natif_C13_sans_email_BE_etranger'] = $view['belgique'] === 6 && $view['etranger'] === 2
            && count($view['liste']->lignes) === 8;
        $checks['CSV_C07_formules'] = false;
        if (count($view['liste']->lignes) === 8) {
            $csv = \Imagine\Pilotage\Envoi\ExportCsv::liste($view['liste']);
            $checks['CSV_C07_formules'] = str_contains($csv, "'=Personnage Fictif C13")
                && str_contains($csv, "'@Ville Fictive") && !str_contains($csv, '@example.org');
        }
        $checks['calcul_historique_testable'] = method_exists(\Imagine\Site\EnvoiNatif::class, 'calculer');
        if ($checks['calcul_historique_testable']) {
            $events = \Imagine\Site\EnvoiNatif::releves((string) get_option('imagine_c13_fixture')['BE']);
            $data = $events[array_key_last($events)]['donnees'];
            $data['creation'] = strtotime('2026-09-01 00:00:00 UTC');
            $data['debut'] = '2026-09-01 00:00:00';
            $data['grace_debut'] = '2026-09-01 00:00:00';
            $data['grace_fin'] = '2026-11-01 00:00:00';
            $base = [['observe_utc' => '2026-10-04 21:59:59.000000', 'donnees' => $data]];
            $before = \Imagine\Site\EnvoiNatif::calculer('DEMO-2026-T4', $base, new \DateTimeImmutable('2026-10-06'));
            $data['rue'] = 'Adresse modifiée après clôture';
            $data['etat'] = 'cancelled';
            $data['creation'] = strtotime('2026-11-01 00:00:00 UTC');
            $after = \Imagine\Site\EnvoiNatif::calculer('DEMO-2026-T4', array_merge($base,
                [['observe_utc' => '2026-10-04 22:00:01.000000', 'donnees' => $data]]), new \DateTimeImmutable('2026-10-07'));
            $checks['gel_cloture_C07_adresse_statut'] = count($before['liste']->lignes) === 1
                && $before['liste']->lignes === $after['liste']->lignes;
            $data['creation'] = strtotime('2026-09-01 00:00:00 UTC');
            $unknown = \Imagine\Site\EnvoiNatif::calculer('DEMO-2026-T4',
                [['observe_utc' => '2026-10-04 22:00:01.000000', 'donnees' => $data]], new \DateTimeImmutable('2026-10-07'));
            $checks['historique_absent_ferme'] = $unknown['historique_incomplet'] && $unknown['liste']->lignes === [];
        }
        $checks['offline_aucun_transport'] = apply_filters('pre_wp_mail', null, ['to' => 'c13@example.org',
            'subject' => 'Sonde passive', 'message' => '', 'headers' => [], 'attachments' => []]) === false
            && is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
            && apply_filters('woocommerce_available_payment_gateways', []) === [];
        $checks['temoins_C13_sans_paiement'] = true;
        foreach (get_option('imagine_c13_fixture') as $subId) {
            $sub = wcs_get_subscription($subId);
            $checks['temoins_C13_sans_paiement'] = $checks['temoins_C13_sans_paiement'] && $sub->is_manual()
                && !$sub->get_date_paid() && !$sub->get_payment_method() && !$sub->get_transaction_id();
        }
        $checks['numero_invalide_refuse'] = false;
        try { \Imagine\Site\EnvoiNatif::apercu('inexistant'); }
        catch (\OutOfBoundsException) { $checks['numero_invalide_refuse'] = true; }
    }
    wp_set_current_user($fixture['users']['E-ABO']);
    $checks['referent_sans_droits_sensibles'] = !current_user_can('manage_options') && !current_user_can('manage_woocommerce')
        && !current_user_can('edit_posts') && !current_user_can('create_users') && !current_user_can('edit_users');
    if ($checks['raccord_natif_et_C07']) {
        $columns = static fn (): array => ['pays', 'destinataire', 'ville'];
        add_filter('pre_option_imagine_envoi_colonnes_export', $columns);
        try {
            $bytes = \Imagine\Site\ListeEnvoiAdmin::preparer('DEMO-2027-T1');
            $checks['format_C10_effectivement_lu'] = str_starts_with($bytes, "pays,destinataire,ville\n")
                && substr_count($bytes, "\n") === 9;
        } finally { remove_filter('pre_option_imagine_envoi_colonnes_export', $columns); }
        global $wpdb;
        $triggered = false;
        $fault = static function (string $sql) use (&$triggered, $wpdb): string {
            if (str_starts_with($sql, 'INSERT INTO') && str_contains($sql, \Imagine\Site\ListeEnvoiAdmin::JOURNAL)) {
                $triggered = true;
                return "SELECT option_id FROM {$wpdb->options} WHERE 1=0";
            }
            return $sql;
        };
        $checks['journal_indisponible_refuse'] = false;
        add_filter('query', $fault);
        try { \Imagine\Site\ListeEnvoiAdmin::preparer('DEMO-2027-T1'); }
        catch (\RuntimeException) { $checks['journal_indisponible_refuse'] = $triggered; }
        finally { remove_filter('query', $fault); }
    }
    $checks['suppression_native_cloture_future'] = false;
    $source = wcs_get_subscription(get_option('imagine_c13_fixture')['BE']);
    $temporary = wcs_create_subscription(['customer_id' => $source->get_customer_id(), 'status' => 'pending',
        'start_date' => gmdate('Y-m-d H:i:s'), 'billing_period' => 'year', 'billing_interval' => 1]);
    if (is_wp_error($temporary)) { throw new \RuntimeException('Témoin de suppression C13 impossible.'); }
    $temporaryId = $temporary->get_id();
    try {
        $temporary->set_requires_manual_renewal(true);
        $temporary->update_meta_data('_imagine_c13_fixture', 'suppression-test');
        $temporary->set_address($source->get_address('shipping'), 'shipping');
        $temporary->update_dates(['end' => '2027-11-01 00:00:00', 'next_payment' => 0], 'gmt');
        $temporary->update_meta_data('_imagine_acces_grace_debut', gmdate('Y-m-d H:i:s'));
        $temporary->update_meta_data('_imagine_acces_grace_fin', '2027-01-06 00:00:00');
        $temporary->set_status('on-hold');
        $temporary->save();
        $temporary->delete(true);
        $v = \Imagine\Site\EnvoiNatif::apercu('DEMO-2027-T1');
        $checks['suppression_native_cloture_future'] = !in_array((string) $temporaryId, array_column($v['liste']->lignes, 'abonnement_id'), true);
    } finally {
        if (wcs_get_subscription($temporaryId)) { wcs_get_subscription($temporaryId)->delete(true); }
        global $wpdb;
        $keys = $wpdb->get_col($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s",
            $wpdb->esc_like(\Imagine\Site\EnvoiNatif::RELEVE . $temporaryId . '_') . '%'));
        foreach ($keys as $key) { delete_option($key); }
        $checks['temoin_suppression_nettoye'] = !wcs_get_subscription($temporaryId)
            && \Imagine\Site\EnvoiNatif::releves((string) $temporaryId) === [];
    }
    wp_set_current_user(0);
    $checks['anonyme_ferme'] = !\Imagine\Site\ListeEnvoiAdmin::autorise();
}
echo wp_json_encode($checks);
