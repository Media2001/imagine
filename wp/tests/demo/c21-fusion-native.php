<?php

declare(strict_types=1);

namespace Imagine\Demo\C21Fusion;

use Imagine\Site\{Confidentialite, ConfidentialiteRegles, CommandeRegles, CommandeNative, EnvoiNatif, EnvoiRegles, ListeEnvoiAdmin, Newsletters, SansEmail};

if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('C21 fictif seulement.');
}
require_once ABSPATH . 'wp-admin/includes/user.php';
global $wpdb;
$tables = $wpdb->get_results('SHOW TABLE STATUS', ARRAY_A);
foreach ($tables as $table) {
    if ($table['Engine'] !== 'InnoDB' || !preg_match('/^[a-zA-Z0-9_]+$/D', $table['Name'])) {
        throw new \RuntimeException('Transaction fictive indisponible.');
    }
}
$fingerprint = static function () use ($wpdb, $tables): array {
    $out = [];
    foreach ($tables as $t) {
        $rows = array_map('serialize', $wpdb->get_results('SELECT * FROM `' . $t['Name'] . '`', ARRAY_A));
        sort($rows, SORT_STRING);
        $out[$t['Name']] = hash('sha256', serialize($rows));
    }
    return $out;
};
$before = $fingerprint();
$checks = [];
$evidence = [];
$wpdb->query('START TRANSACTION');
$guard = static function (string $sql): string {
    if (preg_match('/^\s*(COMMIT|START\s+TRANSACTION|BEGIN|ROLLBACK|CREATE|ALTER|DROP|TRUNCATE|RENAME|LOCK\s+TABLE|UNLOCK\s+TABLE|SET\s+autocommit)\b/i', $sql)) {
        throw new \RuntimeException('Sortie de transaction refusée.');
    }
    return $sql;
};
add_filter('query', $guard, PHP_INT_MAX);
try {
    $make = static function (string $label): int {
        $id = wp_insert_user(['user_login' => 'imagine-c21-fusion-' . $label, 'user_pass' => wp_generate_password(48),
            'user_email' => 'c21-fusion-' . $label . '@example.org', 'display_name' => 'C21 FICTIF ' . $label, 'role' => 'customer']);
        if (is_wp_error($id)) {
            throw new \RuntimeException('Collision fictive.');
        }
        return (int) $id;
    };
    $operator = $make('operateur');
    $client = $make('client');
    wp_set_current_user($operator);
    $address = ['first_name' => 'C21PRENOMCLIENT', 'last_name' => 'C21NOMCLIENT', 'address_1' => '21 RUE CLIENT FICTIVE',
        'address_2' => '', 'postcode' => '1000', 'city' => 'C21VILLECLIENT', 'country' => 'BE'];
    $draft = ['qui' => $operator, 'token' => str_repeat('b', 32), 'etape' => 3,
        'client' => CommandeRegles::client(['mode' => 'nouveau', 'nom' => 'C21NOMCLIENT', 'email' => 'c21-fusion-client@example.org']),
        'commande' => CommandeRegles::commande($address + ['produit' => (string) get_option('imagine_c09_fixture')['tariffs']['normal-1'], 'paiement' => 'bacs'], false)];
    $draft['resultat'] = ['client' => $client];
    $key = 'imagine_c16_brouillon_' . $operator . '_' . $draft['token'];
    set_transient($key, $draft, HOUR_IN_SECONDS);
    $export = Confidentialite::exporter(get_userdata($operator)->user_email);
    $text = wp_json_encode($export, JSON_UNESCAPED_UNICODE);
    $checks['operateur_sans_aucune_PII_client'] = !array_filter(['C21PRENOMCLIENT', 'C21NOMCLIENT', '21 RUE CLIENT FICTIVE', 'C21VILLECLIENT', 'c21-fusion-client@example.org'], static fn ($v) => str_contains($text, $v));
    $checks['operateur_activite_propre_exportee'] = str_contains($text, 'préparé un brouillon');
    Confidentialite::effacer(get_userdata($operator)->user_email);
    $remaining = get_transient($key);
    $checks['effacement_operateur_preserve_dossier_client_exact'] = is_array($remaining)
        && ($remaining['qui'] ?? null) === 0 && array_diff_key($remaining, ['qui' => true]) === array_diff_key($draft, ['qui' => true]);
    $own = Confidentialite::exporter(get_userdata($client)->user_email);
    $ownText = wp_json_encode($own, JSON_UNESCAPED_UNICODE);
    $checks['titulaire_resultat_client_exporte_adresse_exacte'] = str_contains($ownText, '21 RUE CLIENT FICTIVE');
    $checks['mode_reglement_reel_exporte'] = str_contains($ownText, 'Mode de règlement') && str_contains($ownText, 'Virement');
    $evidence['operator_export'] = $export;
    $evidence['client_export'] = $own;
    $evidence['draft_after_operator_erasure'] = $remaining;
    Confidentialite::effacer(get_userdata($client)->user_email);
    $checks['titulaire_efface_brouillon'] = get_transient($key) === false;
    // Vrai créateur C16 : compte neuf sans email, commande et souscription en attente, résultat natif.
    $product = CommandeNative::produits()[get_option('imagine_c09_fixture')['tariffs']['normal-1']];
    foreach (['effacement', 'suppression'] as $mode) {
        $d = $draft;
        $d['token'] = str_replace('-', '', wp_generate_uuid4());
        $d['client'] = CommandeRegles::client(['mode' => 'nouveau', 'nom' => 'C21 SANS EMAIL FICTIF ' . $mode, 'sans_email' => '1']);
        $d['empreinte'] = CommandeNative::empreinte($product);
        $d['resultat'] = CommandeNative::creer($d);
        $uid = $d['resultat']['client'];
        $k = 'imagine_c16_brouillon_' . $operator . '_' . $d['token'];
        set_transient($k, $d, HOUR_IN_SECONDS);
        $out = Confidentialite::exporter(get_userdata($uid)->user_email);
        $checks['C16_sans_email_' . $mode . '_rattachement_reel'] = get_user_meta($uid, SansEmail::META, true) === '1'
            && str_contains(wp_json_encode($out), '21 RUE CLIENT FICTIVE') && wc_get_order($d['resultat']['commande'])->get_status() === 'pending';
        $evidence['C16_' . $mode] = ['resultat' => $d['resultat'], 'export' => $out];
        if ($mode === 'effacement') {
            $r = Confidentialite::effacer(get_userdata($uid)->user_email);
            $checks['C16_sans_email_effacement_transient'] = !$r['items_retained'] && get_transient($k) === false;
        } else {
            $checks['C16_sans_email_suppression_native_transient'] = wp_delete_user($uid) && !get_userdata($uid) && get_transient($k) === false;
        }
    }
    // Les seuls liens cadeau/groupe ci-dessous sont synthétiques C21, jamais des profils C09.
    wp_set_current_user(get_option('imagine_c09_fixture')['users']['E-ADMIN']);
    $owner = $make('payeur');
    $member = $make('membre');
    $other = $make('autre');
    foreach ([$member, $other] as $uid) {
        $customer = new \WC_Customer($uid);
        $customer->set_props(['shipping_first_name' => 'C21 BENEF ' . $uid, 'shipping_last_name' => 'FICTIF',
            'shipping_address_1' => '21 RUE BENEF ' . $uid, 'shipping_postcode' => '1000',
            'shipping_city' => 'FICTIF', 'shipping_country' => 'BE']);
        $customer->save();
    }
    $product = new \WC_Product_Simple();
    $product->set_name('C21 GROUPE FICTIF');
    $product->set_status('private');
    $product->set_regular_price('0');
    $product->save();
    $plan = wp_insert_post(['post_type' => 'wc_membership_plan', 'post_title' => 'C21 PLAN FICTIF', 'post_status' => 'publish']);
    update_post_meta($plan, '_product_ids', [$product->get_id()]);
    $plansFilter = static fn ($plans) => $plans + [$plan => 'groupe'];
    add_filter('option_imagine_acces_plans', $plansFilter);
    $groupsFilter = static fn () => 'liens_memberships';
    add_filter('option_imagine_envoi_groupes', $groupsFilter);
    add_filter('default_option_imagine_envoi_groupes', $groupsFilter);
    $sub = wcs_create_subscription(['customer_id' => $owner, 'status' => 'active', 'start_date' => '2026-01-01 00:00:00',
        'billing_period' => 'year', 'billing_interval' => 1]);
    $sub->set_date_created('2026-01-01 00:00:00');
    $sub->set_date_paid('2026-01-01 00:00:00');
    $sub->add_product($product, 3);
    $sub->save();
    foreach ([$member, $other] as $uid) {
        $m = wc_memberships_create_user_membership(['plan_id' => $plan, 'user_id' => $uid]);
        update_post_meta($m->get_id(), '_subscription_id', $sub->get_id());
    }
    $event = EnvoiNatif::relever($sub);
    $checks['groupe_liens_memberships_natifs_actifs'] = $event['donnees']['origine'] === 'groupe'
        && $event['donnees']['beneficiaires_resolus'] === true
        && array_column($event['donnees']['beneficiaires'], 'id') === [(string) $member, (string) $other];
    // Horodatage historique explicitement synthétique, limité à notre gel C21.
    $event['observe_utc'] = '2026-01-02 00:00:00.000000';
    $calendar = get_option(EnvoiNatif::CALENDRIER);
    $calendar[0]['code'] = 'C21-FUSION-GROUPE';
    $now = new \DateTimeImmutable('now', new \DateTimeZone('UTC'));
    $snapshot = EnvoiRegles::figer('C21-FUSION-GROUPE', [$event], $now, $calendar);
    add_option(EnvoiNatif::GEL . 'C21-FUSION-GROUPE', $snapshot, '', false);
    $beforeList = EnvoiNatif::apercu('C21-FUSION-GROUPE')['liste']->lignes;
    $beforeCsv = ListeEnvoiAdmin::preparer('C21-FUSION-GROUPE');
    $beforeOther = Confidentialite::exporter(get_userdata($other)->user_email);
    Confidentialite::effacer(get_userdata($member)->user_email);
    $view = EnvoiNatif::apercu('C21-FUSION-GROUPE');
    $csv = ListeEnvoiAdmin::preparer('C21-FUSION-GROUPE');
    $expected = array_values(array_filter($beforeList, static fn ($r) => $r['destinataire_id'] === (string) $other));
    $checks['gel_reel_retrait_membre_tiers_lignes_exactes'] = count($beforeList) === 2 && count($expected) === 1
        && $view['liste']->lignes === $expected && !$view['historique_incomplet'];
    $checks['CSV_reel_retrait_membre_tiers_servi'] = str_contains($csv, '21 RUE BENEF ' . $other)
        && !str_contains($csv, '21 RUE BENEF ' . $member);
    $afterOther = Confidentialite::exporter(get_userdata($other)->user_email);
    $checks['export_beneficiaire_retrait_autre_sans_perte_exact'] = $beforeOther === $afterOther;
    Confidentialite::effacer(get_userdata($owner)->user_email);
    $afterOwner = EnvoiNatif::apercu('C21-FUSION-GROUPE');
    $csvOwner = ListeEnvoiAdmin::preparer('C21-FUSION-GROUPE');
    $checks['gel_reel_retrait_payeur_groupe_tiers_exact'] = $afterOwner['liste']->lignes === $expected
        && !$afterOwner['historique_incomplet'] && $csvOwner === $csv;
    $checks['export_beneficiaire_retrait_payeur_sans_perte_exact'] = $afterOther === Confidentialite::exporter(get_userdata($other)->user_email);
    $evidence['groupe'] = ['native' => $event, 'gel_before' => $snapshot, 'lines_before' => $beforeList,
        'CSV_before' => $beforeCsv, 'lines_after' => $afterOwner['liste']->lignes, 'CSV_after' => $csvOwner,
        'export_tiers_before' => $beforeOther, 'export_tiers_after' => Confidentialite::exporter(get_userdata($other)->user_email)];
    // Cadeau natif : l'adresse de livraison est celle du bénéficiaire, non du payeur.
    $giftOwner = $make('offrant');
    $gift = wcs_create_subscription(['customer_id' => $giftOwner, 'status' => 'active', 'start_date' => '2026-01-01 00:00:00',
        'billing_period' => 'year', 'billing_interval' => 1]);
    $gift->set_date_created('2026-01-01 00:00:00');
    $gift->set_date_paid('2026-01-01 00:00:00');
    $gift->set_address($address, 'shipping');
    $gift->update_meta_data('_recipient_user', $other);
    $gift->save();
    $giftEvent = EnvoiNatif::relever($gift);
    $giftEvent['observe_utc'] = '2026-01-02 00:00:00.000000';
    $calendar[0]['code'] = 'C21-FUSION-CADEAU';
    add_option(EnvoiNatif::GEL . 'C21-FUSION-CADEAU', EnvoiRegles::figer('C21-FUSION-CADEAU', [$giftEvent], $now, $calendar), '', false);
    $giftBefore = EnvoiNatif::apercu('C21-FUSION-CADEAU')['liste']->lignes;
    $giftCsv = ListeEnvoiAdmin::preparer('C21-FUSION-CADEAU');
    $otherExport = Confidentialite::exporter(get_userdata($other)->user_email);
    Confidentialite::effacer(get_userdata($giftOwner)->user_email);
    $checks['offrant_efface_cadeau_postal_exact'] = count($giftBefore) === 1
        && EnvoiNatif::apercu('C21-FUSION-CADEAU')['liste']->lignes === $giftBefore
        && ListeEnvoiAdmin::preparer('C21-FUSION-CADEAU') === $giftCsv;
    $checks['offrant_efface_export_beneficiaire_exact'] = $otherExport === Confidentialite::exporter(get_userdata($other)->user_email);
    $checks['export_tiers_pas_identite_payeur_ni_autre_membre'] = !str_contains(wp_json_encode($otherExport), 'c21-fusion-offrant@example.org')
        && !str_contains(wp_json_encode($otherExport), '21 RUE BENEF ' . $member);
    $evidence['cadeau'] = ['native' => $giftEvent, 'lines_before' => $giftBefore, 'CSV_before' => $giftCsv,
        'lines_after' => EnvoiNatif::apercu('C21-FUSION-CADEAU')['liste']->lignes,
        'CSV_after' => ListeEnvoiAdmin::preparer('C21-FUSION-CADEAU'), 'export_before' => $otherExport,
        'export_after' => Confidentialite::exporter(get_userdata($other)->user_email)];
    foreach ([$owner, $member, $giftOwner] as $uid) {
        $rid = wp_create_user_request(get_userdata($uid)->user_email, 'remove_personal_data');
        wp_update_post(['ID' => $rid, 'post_author' => $uid, 'post_status' => 'request-completed']);
    }
    $freshGroup = EnvoiNatif::relever($sub);
    $freshGift = EnvoiNatif::relever($gift);
    $checks['recollecte_payeur_et_membre_effaces_ne_reviennent_pas'] = $freshGroup['donnees']['user'] === '0'
        && array_column($freshGroup['donnees']['beneficiaires'], 'id') === [(string) $other]
        && $freshGroup['donnees']['beneficiaires_resolus'] === true && $freshGift['donnees']['user'] === '0'
        && $freshGift['donnees']['beneficiaires'] === $giftEvent['donnees']['beneficiaires'];
    $evidence['fresh_after_completed_requests'] = [$freshGroup, $freshGift];
    remove_filter('option_imagine_acces_plans', $plansFilter);
    remove_filter('option_imagine_envoi_groupes', $groupsFilter);
    update_user_meta($client, Newsletters::META, ['C21-fictif' => true]);
    $export = Confidentialite::exporter(get_userdata($client)->user_email);
    $checks['meta_constantes_connues_couvertes'] = str_contains(wp_json_encode($export), Newsletters::META);
    Confidentialite::effacer(get_userdata($client)->user_email);
    $checks['meta_C22_effacee'] = !metadata_exists('user', $client, Newsletters::META);
} finally {
    remove_filter('query', $guard, PHP_INT_MAX);
    $wpdb->query('ROLLBACK');
    wp_cache_flush();
}
$checks['rollback_toutes_tables_exact'] = $before === $fingerprint();
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => array_keys(array_filter($checks, static fn ($v): bool => $v !== true)), 'evidence' => $evidence]);
