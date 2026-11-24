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
        $checks['aucun_paiement_invente_C09'] = ($excluded[(string) $fixture['subscriptions']['A-SANSMAIL']] ?? '') === 'paiement_non_valide';
        $checks['repartition_exacte'] = $view['belgique'] + $view['etranger'] === count($view['liste']->lignes);
        $checks['positif_natif_C13_sans_email_BE_etranger'] = $view['belgique'] === 1 && $view['etranger'] === 1
            && count($view['liste']->lignes) === 2;
        $checks['CSV_C07_formules'] = false;
        if (count($view['liste']->lignes) === 2) {
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
                && substr_count($bytes, "\n") === 3;
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
    wp_set_current_user(0);
    $checks['anonyme_ferme'] = !\Imagine\Site\ListeEnvoiAdmin::autorise();
}
echo wp_json_encode($checks);
