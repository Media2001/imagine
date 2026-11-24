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
        $checks['numero_invalide_refuse'] = false;
        try { \Imagine\Site\EnvoiNatif::apercu('inexistant'); }
        catch (\OutOfBoundsException) { $checks['numero_invalide_refuse'] = true; }
    }
    wp_set_current_user(0);
    $checks['anonyme_ferme'] = !\Imagine\Site\ListeEnvoiAdmin::autorise();
}
echo wp_json_encode($checks);
