<?php
/** Recette réelle B02 : lecture des objets installés, aucune fabrication de paiement. */
declare(strict_types=1);

use Imagine\Site\MonCompte;
use Imagine\Site\Paywall;
use Imagine\Site\EnvoiNatif;

if (get_option('imagine_demo_site') !== 'imagine-test-demo' || wp_get_environment_type() !== 'local') {
    throw new RuntimeException('Cible B02 refusée.');
}
$checks = ['raccord_mon_compte_present' => class_exists(MonCompte::class)];
if (!$checks['raccord_mon_compte_present']) {
    echo wp_json_encode($checks);
    return;
}
$f = get_option('imagine_c09_fixture');
foreach (['A-CARTE', 'A-SEPA4', 'A-SUSP', 'P-NUMERO', 'V-INSCRIT'] as $who) {
    wp_set_current_user($f['users'][$who]);
    Paywall::invalidate();
    $v = MonCompte::donnees();
    $checks[$who . '_proprietaire_session'] = $v['user'] === $f['users'][$who];
    foreach ($v['abonnements'] as $row) {
        $s = wcs_get_subscription($row['id']);
        $checks[$who . '_abonnement_' . $row['id'] . '_natif_propre'] = (int) $s->get_customer_id() === $v['user'];
        $checks[$who . '_adresse_' . $row['id'] . '_source_postale'] = $row['adresse'] === $s->get_address('shipping');
        $checks[$who . '_aucun_paiement_invente'] = $row['paiement'] === 'Moyen de paiement non raccordé';
        $first = $who === 'A-CARTE' ? 'DEMO-2026-T4' : ($who === 'A-SEPA4' ? 'DEMO-2026-T3' : 'DEMO-2026-T1');
        $last = $who === 'A-CARTE' ? 'DEMO-2027-T3' : ($who === 'A-SEPA4' ? 'DEMO-2027-T2' : 'DEMO-2026-T4');
        $checks[$who . '_range_C01'] = $row['premier'] === $first && $row['dernier'] === $last;
        $checks[$who . '_compteur_historique_nomme'] = $row['restants'] === null;
    }
    foreach ($v['numeros'] as $n) {
        $checks[$who . '_PDF_' . $n['id'] . '_decision_C11'] = Paywall::decisionPdf(get_post($n['id']))['complet'] === true
            && $n['pdf'] === home_url('/?imagine_pdf=' . $n['id']);
    }
    ob_start();
    MonCompte::afficher();
    $html = ob_get_clean();
    foreach (['abonnement', 'echeances', 'numeros', 'coordonnees', 'factures'] as $section) {
        $checks[$who . '_section_' . $section] = str_contains($html, 'id="imagine-compte-' . $section . '"');
    }
    preg_match('/<ul data-imagine-factures>(.*?)<\/ul>/s', $html, $factures);
    preg_match('/<div data-imagine-justificatif>(.*?)<\/div>/s', $html, $justificatif);
    $checks[$who . '_factures_vides_explicites'] = $v['factures'] === []
        && isset($factures[1]) && str_contains($factures[1], 'Aucune facture disponible')
        && str_contains($factures[1], 'raccord documentaire Odoo non disponible');
    $checks[$who . '_justificatif_session_distinct'] = isset($justificatif[1])
        && str_contains($justificatif[1], 'name="justificatif"')
        && str_contains($justificatif[1], 'value="' . Imagine\Site\Justificatifs::version(Imagine\Site\Justificatifs::etat($v['user'])) . '"');
    $checks[$who . '_factures_sans_melange_justificatif'] = isset($factures[1], $justificatif[1])
        && !str_contains($factures[1], 'justificatif') && !str_contains($factures[1], '<a ')
        && !str_contains($justificatif[1], 'data-imagine-factures')
        && str_contains($html, 'Les commandes ne sont pas présentées comme des factures.');
    if ($who === 'A-CARTE') {
        $checks['gel_postal_non_atteste_par_B02'] = !str_contains($html, 'Une liste déjà close conserve son instantané.');
        $checks['carte_actif_natif_sans_carte_inventee'] = $v['abonnements'][0]['etat'] === 'Actif';
        $checks['carte_montant_date_natifs'] = $v['abonnements'][0]['prochaine'] === wcs_get_subscription($f['subscriptions'][$who])->get_date('next_payment', 'gmt')
            && $v['abonnements'][0]['montant'] === '120.00';
    }
    if ($who === 'A-SEPA4') {
        $checks['quatre_positions_meme_sans_marge'] = count($v['abonnements'][0]['echeances']) === 4;
        $checks['marge_manquante_sans_dates_inventees'] = count(array_filter($v['abonnements'][0]['echeances'], static fn ($e) => $e['date'] === null)) === 4;
        $states = array_column($v['abonnements'][0]['echeances'], 'etat');
        $checks['deux_payees_deux_a_venir_modele'] = $states === ['Payée', 'Payée', 'À venir', 'À venir'];
        $checks['deux_payees_deux_a_venir_rendu'] = substr_count($html, '>Payée<') === count(array_filter($states, static fn ($s) => $s === 'Payée'))
            && substr_count($html, '>À venir<') === 2;
        $known = array_values(array_filter($v['abonnements'][0]['echeances'], static fn ($e) => ($e['commande'] ?? null) !== null));
        $checks['reglements_identifiants_montants_propres'] = count($known) === 2;
        foreach ($known as $entry) {
            $native = wc_get_order($entry['commande']);
            $checks['reglements_identifiants_montants_propres'] = $checks['reglements_identifiants_montants_propres']
                && (int) $native->get_customer_id() === $v['user'] && $entry['montant'] === $native->get_total()
                && $entry['devise'] === $native->get_currency();
        }
        $checks['lecture_rejouee_sans_double_compte'] = MonCompte::donnees()['abonnements'][0]['echeances'] === $v['abonnements'][0]['echeances'];
        $checks['deux_paiements_natifs_C09'] = wcs_get_subscription($f['subscriptions'][$who])->get_payment_count() === 2;
    }
    if ($who === 'A-SUSP') {
        $checks['suspendu_clair'] = $v['abonnements'][0]['etat'] === 'Suspendu';
        $checks['suspendu_bandeau_action_native_rejet_fictif'] = str_contains($html, 'data-imagine-regularisation')
            && str_contains($html, '/view-subscription/' . $f['subscriptions'][$who]) && str_contains($html, 'Échéance échouée');
        $checks['suspendu_aucun_PDF'] = $v['numeros'] === [];
    }
    if ($who === 'P-NUMERO') {
        $checks['achat_C14_numero_unique'] = count($v['numeros']) === 1 && $v['numeros'][0]['id'] === get_option('imagine_demo_manifest')['demo-2026-t1'];
    }
}
wp_set_current_user(0);
$checks['anonyme_modele_vide'] = MonCompte::donnees() === [];
ob_start(); MonCompte::afficher(); $html = ob_get_clean();
$checks['anonyme_pas_de_coordonnees'] = $html === '';
$checks['profil_reception_A_SEPA4_natif'] = isset($f['subscriptions']['A-SEPA4']) && (bool) get_user_by('login', 'a-sepa4');
echo wp_json_encode($checks, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
