<?php
/** C13 correction : liens natifs jetables et restauration exacte ; aucun appel de paiement. */
declare(strict_types=1);
namespace Imagine\Demo\C13Corrections;

use Imagine\Site\{EnvoiNatif, EnvoiRelations, EnvoiRegles, ListeEnvoiAdmin};

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new \RuntimeException('Cible refusée.');
}
$checks = ['regles_pures_presentes' => class_exists(EnvoiRegles::class),
    'relations_natives_presentes' => class_exists(EnvoiRelations::class)];
if (!array_product($checks)) { echo wp_json_encode($checks); return; }
$oldPlans = get_option('imagine_acces_plans');
$oldPolicy = get_option('imagine_envoi_groupes', null);
$manifest = get_option('imagine_c13_fixture');
$source = wcs_get_subscription($manifest['BE']);
$recipient = wcs_get_subscription($manifest['FR']);
$sub = null;
$product = null;
$order = null;
$memberIds = [];
$planId = 0;
$oldAddresses = [];
$gelKey = EnvoiNatif::GEL . 'C13-GEL-FICTIF';
if (get_option($gelKey, null) !== null) { throw new \RuntimeException('Collision de gel jetable.'); }
$owned = '_imagine_c13_correction_jetable';
try {
    $sub = wcs_create_subscription(['customer_id' => $source->get_customer_id(), 'status' => 'pending',
        'start_date' => '2026-01-01 00:00:00', 'billing_period' => 'year', 'billing_interval' => 1]);
    if (is_wp_error($sub)) { throw new \RuntimeException('Souscription jetable impossible.'); }
    $sub->update_meta_data($owned, 'fictif');
    $sub->set_requires_manual_renewal(true);
    $sub->set_address($recipient->get_address('shipping'), 'shipping');
    $sub->update_meta_data('_recipient_user', $recipient->get_customer_id());
    $sub->save();
    $gift = EnvoiNatif::relever(wcs_get_subscription($sub->get_id()));
    $checks['cadeau_relation_native_identite_adresse'] = $gift['donnees']['origine'] === 'offert'
        && $gift['donnees']['beneficiaires_resolus']
        && $gift['donnees']['beneficiaires'][0]['id'] === (string) $recipient->get_customer_id()
        && $gift['donnees']['beneficiaires'][0]['rue'] === $recipient->get_shipping_address_1();
    $sub->update_meta_data('_recipient_user', (string) $recipient->get_customer_id() . '-invalide');
    $sub->save();
    $malformedGift = EnvoiNatif::relever($sub);
    $checks['identifiant_beneficiaire_malforme_pas_normalise'] = $malformedGift['donnees']['origine'] === 'offert'
        && !$malformedGift['donnees']['beneficiaires_resolus'] && $malformedGift['donnees']['beneficiaires'] === [];
    $sub->delete_meta_data('_recipient_user');
    $sub->update_meta_data('_recipient_user_email_address', 'beneficiaire-absent-fictif@example.org');
    $sub->save();
    $missing = EnvoiNatif::relever($sub);
    $checks['cadeau_incomplet_ferme_sans_rapprochement_email'] = $missing['donnees']['origine'] === 'offert'
        && !$missing['donnees']['beneficiaires_resolus'] && $missing['donnees']['beneficiaires'] === [];
    $sub->delete_meta_data('_recipient_user_email_address');
    $product = new \WC_Product_Simple();
    $product->set_name('C13 produit collectif FICTIF jetable');
    $product->set_status('private');
    $product->set_regular_price('0');
    $product->update_meta_data($owned, 'fictif');
    $product->save();
    $sub->add_product($product, 3);
    $sub->save();
    $planId = wp_insert_post(['post_type' => 'wc_membership_plan', 'post_status' => 'publish',
        'post_title' => 'C13 groupe FICTIF jetable', 'meta_input' => [$owned => 'fictif',
            '_access_method' => 'purchase', '_product_ids' => [$product->get_id()]]], true);
    if (is_wp_error($planId)) { throw new \RuntimeException('Plan jetable impossible.'); }
    update_option('imagine_acces_plans', $oldPlans + [$planId => 'groupe']);
    foreach ([$source, $recipient] as $index => $origin) {
        $uid = $origin->get_customer_id();
        $customer = new \WC_Customer($uid);
        $oldAddresses[$uid] = [];
        foreach (['first_name', 'last_name', 'address_1', 'address_2', 'postcode', 'city', 'country'] as $key) {
            $method = 'get_shipping_' . $key;
            $oldAddresses[$uid][$key] = $customer->$method();
            $method = 'set_shipping_' . $key;
            $customer->$method($origin->get_address('shipping')[$key]);
        }
        $customer->save();
        $membership = wc_memberships_create_user_membership(['plan_id' => $planId, 'user_id' => $uid]);
        if (is_wp_error($membership)) { throw new \RuntimeException('Attribution native impossible.'); }
        $memberIds[] = $membership->get_id();
        update_post_meta($membership->get_id(), $owned, 'fictif');
        update_post_meta($membership->get_id(), '_subscription_id', $sub->get_id());
        $membership->update_status('active');
    }
    update_option('imagine_envoi_groupes', 'ferme');
    $closed = EnvoiNatif::relever($sub);
    $checks['politique_groupes_defaut_ferme'] = !$closed['donnees']['beneficiaires_resolus'];
    update_option('imagine_envoi_groupes', 'liens_memberships');
    $group = EnvoiNatif::relever($sub);
    $checks['groupe_natif_deux_attribuees_une_libre'] = $group['donnees']['origine'] === 'groupe'
        && $group['donnees']['places'] === 3 && $group['donnees']['beneficiaires_resolus']
        && count($group['donnees']['beneficiaires']) === 2;
    update_option('imagine_acces_plans', $oldPlans + [$planId => 'offert']);
    $requiredGift = EnvoiNatif::relever($sub);
    $checks['cadeau_requis_sans_relation_ferme_pas_payeur'] = $requiredGift['donnees']['origine'] === 'offert'
        && !$requiredGift['donnees']['beneficiaires_resolus'] && $requiredGift['donnees']['beneficiaires'] === [];
    update_option('imagine_acces_plans', $oldPlans + [$planId => 'groupe']);
    EnvoiNatif::relever($sub);
    $history = EnvoiNatif::releves((string) $sub->get_id());
    $checks['attributions_historisees_append_only'] = in_array($gift, $history, true)
        && in_array($missing, $history, true) && in_array($closed, $history, true) && in_array($group, $history, true);
    $count = count($history);
    EnvoiNatif::relever($sub);
    $checks['observation_rejouee_sans_doublon'] = count(EnvoiNatif::releves((string) $sub->get_id())) === $count;
    $changedCustomer = new \WC_Customer($recipient->get_customer_id());
    $changedCustomer->set_shipping_address_1('Adresse fictive modifiee par CRUD C13');
    $changedCustomer->save();
    $observed = EnvoiNatif::releves((string) $sub->get_id());
    $checks['adresse_beneficiaire_hook_natif_historise'] = count($observed) > $count && in_array($group, $observed, true)
        && $observed[array_key_last($observed)]['donnees']['beneficiaires'][1]['rue'] === 'Adresse fictive modifiee par CRUD C13';
    // Commande de renouvellement native à zéro, date/statut explicitement fictifs, jamais payment_complete().
    $order = wc_create_order(['customer_id' => $sub->get_customer_id(), 'status' => 'pending']);
    if (is_wp_error($order)) { throw new \RuntimeException('Commande jetable impossible.'); }
    $order->update_meta_data($owned, 'fictif');
    $order->update_meta_data('_subscription_renewal', $sub->get_id());
    $order->set_payment_method('');
    $order->set_transaction_id('');
    $order->set_total('0');
    $order->set_date_paid(null);
    $order->save();
    $checks['renouvellement_attente_non_reconnu'] = EnvoiRelations::renouvellements($sub) === [];
    $order->set_status('completed');
    $order->set_date_paid('2026-11-01 00:00:00');
    $order->save();
    $renewed = EnvoiNatif::relever(wcs_get_subscription($sub->get_id()));
    $checks['renouvellement_annuel_enregistre_sans_deplacer_date'] = count($renewed['donnees']['renouvellements']) === 1
        && $renewed['donnees']['debut'] === '2026-01-01 00:00:00'
        && $renewed['donnees']['renouvellements'][0]['id'] === (string) $order->get_id();

    $checks['renouvellement_pas_paiement_initial_reconstruit'] = $renewed['donnees']['paiement'] === null;
    $nativeView = EnvoiNatif::calculer('DEMO-2027-T1', EnvoiNatif::releves((string) $sub->get_id()),
        new \DateTimeImmutable('now', new \DateTimeZone('UTC')));
    $checks['renouvellement_natif_C01_C07_deux_beneficiaires'] = count($nativeView['liste']->lignes) === 2
        && array_unique(array_column($nativeView['liste']->lignes, 'origine')) === ['groupe'];
    $sub->set_billing_period('month');
    $sub->set_billing_interval(3);
    $sub->save();
    $checks['echeance_trimestrielle_pas_nouvelle_annee'] = EnvoiRelations::renouvellements($sub) === [];
    $order->update_meta_data('_imagine_envoi_bloc_debut', '2026-11-01 00:00:00');
    $order->save();
    $checks['bloc_explicitement_enregistre_reconnu'] = count(EnvoiRelations::renouvellements($sub)) === 1;
    $checks['aucune_transaction_effectuee'] = !$order->get_transaction_id() && !$order->get_payment_method()
        && (float) $order->get_total() === 0.0;
    $calendar = get_option('imagine_demo_calendrier');
    $changed = $calendar;
    $changed[0]['cloture'] = '2026-01-07';
    update_option('imagine_demo_calendrier', $changed);
    $checks['cloture_passee_reecriture_option_refusee'] = get_option('imagine_demo_calendrier') === $calendar
        && get_option(EnvoiNatif::CALENDRIER) === $calendar;
    update_option(EnvoiNatif::CALENDRIER, $changed);
    $checks['reference_passee_reecriture_directe_refusee'] = get_option(EnvoiNatif::CALENDRIER) === $calendar;
    // Entrées pures fictives, jamais des relevés natifs antidatés.
    $rows = [];
    foreach ([1, 4, 7, 10] as $index => $month) {
        $rows[] = ['code' => $index === 0 ? 'C13-GEL-FICTIF' : 'C13-GEL-' . $index,
            'type' => 'regulier', 'sortie' => sprintf('2026-%02d-15', $month),
            'cloture' => sprintf('2026-%02d-05', $month)];
    }
    $synthetic = $gift['donnees'];
    $synthetic['creation'] = strtotime('2026-01-01 UTC');
    $synthetic['debut'] = '2026-01-01 00:00:00';
    $synthetic['etat'] = 'active';
    $synthetic['paiement'] = strtotime('2026-01-01 UTC');
    $snapshot = EnvoiRegles::figer('C13-GEL-FICTIF', [['observe_utc' => '2026-01-02 00:00:00', 'donnees' => $synthetic]],
        new \DateTimeImmutable('2026-02-01 UTC'), $rows);
    if (!add_option($gelKey, $snapshot, '', false) || get_option($gelKey) !== $snapshot) {
        throw new \RuntimeException('Gel fictif non persisté/relu.');
    }
    $before = EnvoiNatif::apercu('C13-GEL-FICTIF');
    $poison = static fn (): array => [];
    add_filter('pre_option_' . EnvoiNatif::CALENDRIER, $poison);
    add_filter('pre_option_imagine_demo_calendrier', $poison);
    try {
        $after = EnvoiNatif::apercu('C13-GEL-FICTIF');
        $checks['gel_persistant_ignore_calendrier_courant'] = count($before['liste']->lignes) === 1
            && $before['liste']->lignes === $after['liste']->lignes && $before['blocs'] === $after['blocs'];
    } finally {
        remove_filter('pre_option_' . EnvoiNatif::CALENDRIER, $poison);
        remove_filter('pre_option_imagine_demo_calendrier', $poison);
    }
    update_option($gelKey, ['version' => 'corrompue']);
    $checks['gel_persistant_reecriture_refusee'] = get_option($gelKey) === $snapshot;
    $checks['libelle_non_eligible_traduit'] = ListeEnvoiAdmin::motif('non_eligible') === 'Non éligible à l’envoi';
} finally {
    foreach ($memberIds as $id) { wp_delete_post($id, true); }
    delete_option($gelKey);
    $checks['gel_jetable_absent'] = get_option($gelKey, null) === null;
    if ($order && !is_wp_error($order)) { $order->delete(true); }
    if ($sub && !is_wp_error($sub)) {
        $id = (string) $sub->get_id();
        $sub->delete(true);
        global $wpdb;
        foreach ($wpdb->get_col($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s",
            $wpdb->esc_like(EnvoiNatif::RELEVE . $id . '_') . '%')) as $key) { delete_option($key); }
        $checks['souscription_jetable_nettoyee'] = !wcs_get_subscription($id) && EnvoiNatif::releves($id) === [];
    }
    if ($product) { $product->delete(true); }
    if ($planId && !is_wp_error($planId)) { wp_delete_post($planId, true); }
    foreach ($oldAddresses as $uid => $address) {
        $customer = new \WC_Customer($uid);
        foreach ($address as $key => $value) { $method = 'set_shipping_' . $key; $customer->$method($value); }
        $customer->save();
        foreach ($address as $key => $value) { $method = 'get_shipping_' . $key;
            if ((new \WC_Customer($uid))->$method() !== $value) { throw new \RuntimeException('Adresse non restaurée.'); } }
    }
    update_option('imagine_acces_plans', $oldPlans);
    if ($oldPolicy === null) { delete_option('imagine_envoi_groupes'); }
    else { update_option('imagine_envoi_groupes', $oldPolicy); }
    $checks['options_restaurees'] = get_option('imagine_acces_plans') === $oldPlans
        && get_option('imagine_envoi_groupes', null) === $oldPolicy;
    $checks['objets_jetables_absents'] = !$product || !wc_get_product($product->get_id());
    $checks['objets_jetables_absents'] = $checks['objets_jetables_absents']
        && (!$order || !wc_get_order($order->get_id())) && (!$planId || !get_post($planId));
    foreach ($memberIds as $id) { $checks['objets_jetables_absents'] = $checks['objets_jetables_absents'] && !get_post($id); }
}
echo wp_json_encode($checks);
