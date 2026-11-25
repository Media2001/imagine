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
        $checks[$who . '_range_C01'] = $row['premier'] === 'DEMO-2026-T1' && $row['dernier'] === 'DEMO-2026-T4';
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
    $checks[$who . '_factures_vides_explicites'] = $v['factures'] === [] && str_contains($html, 'Aucune facture ou justificatif disponible');
    if ($who === 'A-CARTE') {
        $checks['carte_actif_natif_sans_carte_inventee'] = $v['abonnements'][0]['etat'] === 'Actif';
        $checks['carte_montant_date_natifs'] = $v['abonnements'][0]['prochaine'] === wcs_get_subscription($f['subscriptions'][$who])->get_date('next_payment', 'gmt')
            && $v['abonnements'][0]['montant'] === '120.00';
    }
    if ($who === 'A-SEPA4') {
        $checks['quatre_positions_meme_sans_marge'] = count($v['abonnements'][0]['echeances']) === 4;
        $checks['marge_manquante_sans_dates_inventees'] = count(array_filter($v['abonnements'][0]['echeances'], static fn ($e) => $e['date'] === null)) === 4;
        $checks['quatre_non_marquees_payees'] = !str_contains($html, '>Payée<');
    }
    if ($who === 'A-SUSP') {
        $checks['suspendu_clair'] = $v['abonnements'][0]['etat'] === 'Suspendu';
        $checks['suspendu_bandeau_action_native_sans_rejet_invente'] = str_contains($html, 'data-imagine-regularisation')
            && str_contains($html, '/view-subscription/' . $f['subscriptions'][$who]) && !str_contains($html, 'Échéance échouée');
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
$checks['A_4x_J45_absent_pas_de_profil_fabrique'] = !get_user_by('login', 'a-4x-j45');
echo wp_json_encode($checks, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
