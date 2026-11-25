<?php
/** États natifs supplémentaires, lecture seule ; aucune date/statut modifié. */
declare(strict_types=1);
use Imagine\Site\MonCompte;
$f = get_option('imagine_c09_fixture');
$checks = [];
foreach (['A-VIR' => 'Virement en attente de validation', 'A-EXPIRE' => 'Expiré', 'A-NONRENOUV' => 'Actif'] as $who => $expected) {
    $sub = wcs_get_subscription($f['subscriptions'][$who]);
    $checks[$who . '_etat_natif_clair'] = MonCompte::etat($sub) === $expected;
}
$sub = wcs_get_subscription($f['subscriptions']['A-GRACE']);
$now = gmdate('Y-m-d H:i:s');
$from = $sub->get_meta('_imagine_acces_grace_debut');
$until = $sub->get_meta('_imagine_acces_grace_fin');
$expected = $from <= $now && $now < $until ? 'En délai de grâce' : 'Suspendu';
$checks['grace_fenetre_UTC_native_pas_renouvelee'] = MonCompte::etat($sub) === $expected;
$checks['API_identite_aucun_argument'] = (new ReflectionMethod(MonCompte::class, 'donnees'))->getNumberOfParameters() === 0;
$checks['hook_subscription_postal_natif_present'] = (bool) has_action('woocommerce_after_subscription_object_save');
$outside = true;
foreach ($GLOBALS['wp_filter']['woocommerce_after_subscription_object_save']->callbacks as $callbacks) {
    foreach ($callbacks as $cb) {
        if ($cb['function'] instanceof Closure && basename((new ReflectionFunction($cb['function']))->getFileName()) === 'MonCompte.php') {
            try {
                // Objet natif non persisté : hors formulaire B02, notre callback ne doit rien observer.
                ($cb['function'])(new WC_Subscription());
            } catch (Throwable) {
                $outside = false;
            }
        }
    }
}
$checks['raccord_postal_hors_formulaire_sans_effet'] = $outside;
$failed = 0;
foreach (['A-CARTE', 'A-SEPA4', 'A-SUSP'] as $who) {
    $sub = wcs_get_subscription($f['subscriptions'][$who]);
    foreach (array_unique([$sub->get_parent_id(), ...array_values($sub->get_related_orders('ids', 'renewal'))]) as $id) {
        $o = wc_get_order($id);
        $failed += $o && $o->has_status('failed') ? 1 : 0;
    }
}
$checks['aucun_rejet_natif_ne_pas_fabriquer'] = $failed === 0;
echo wp_json_encode($checks, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
