<?php
/** C09 : recette native en lecture seule, chaque assertion est exportée. */
declare(strict_types=1);
namespace Imagine\Demo\C09Tests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible C09 refusée.');
}
$checks = [];
$fixture = get_option('imagine_c09_fixture', []);
$rows = json_decode(file_get_contents(WP_CONTENT_DIR . '/imagine-demo-build/c09-profils.json'), true, 512, JSON_THROW_ON_ERROR);
$checks['catalogue_30'] = count($rows) === 30;
$checks['fixture_installee'] = isset($fixture['users']) && count($fixture['users']) === 27;
$proof = [];
if ($checks['fixture_installee']) {
    $secret = json_decode(file_get_contents('/var/www/.imagine-demo/seed-secret.json'), true, 512, JSON_THROW_ON_ERROR);
    $post = get_post(get_option('imagine_c08_fixture')['article']);
    foreach ($rows as $row) {
        $key = $row['code'];
        if ($key === 'V-ROBOT') { continue; }
        $id = (int) ($fixture['users'][$key] ?? 0);
        wp_set_current_user($id);
        $_SERVER['REMOTE_ADDR'] = '192.0.2.9';
        $_SERVER['HTTP_USER_AGENT'] = $key === 'V-FAUX' ? 'Googlebot/2.1' : 'Imagine C09 recette locale';
        $decision = \Imagine\Site\Paywall::decision($post);
        $entry = ['user_id' => $id, 'decision' => $decision, 'orders' => [], 'subscriptions' => [], 'memberships' => []];
        $checks[$key . ':motif'] = $decision['motif'] === $row['motif'];
        if (!$row['compte']) {
            $checks[$key . ':sans_compte'] = !$id && !get_user_by('login', strtolower($key));
            $proof[$key] = $entry;
            continue;
        }
        $account = $secret['c09_accounts'][$key];
        $user = get_userdata($id);
        $checks[$key . ':login_email'] = $user && $user->user_login === strtolower($key) && $user->user_email === strtolower($key) . '@example.org';
        $checks[$key . ':password'] = $user && wp_check_password($account['password'], $user->user_pass, $id);
        $checks[$key . ':role'] = $user && $user->roles === [$row['role'] ?? 'customer'];
        $orders = wc_get_orders(['customer_id' => $id, 'type' => 'shop_order', 'limit' => -1]);
        $subs = wcs_get_users_subscriptions($id);
        $members = wc_memberships_get_user_memberships($id, ['status' => 'any']) ?? [];
        $checks[$key . ':nombre_commandes'] = count($orders) === ((isset($row['native']) || !empty($row['order_only'])) ? 1 : 0);
        $checks[$key . ':nombre_abonnements'] = count($subs) === (isset($row['native']) ? 1 : 0);
        $checks[$key . ':nombre_adhesions'] = count($members) === ((isset($row['native']) || isset($row['membership'])) ? 1 : 0);
        foreach ($orders as $order) {
            $entry['orders'][] = ['id' => $order->get_id(), 'status' => $order->get_status(), 'total' => $order->get_total(),
                'customer_id' => $order->get_customer_id(), 'item_count' => $order->get_item_count(), 'date_paid' => $order->get_date_paid(),
                'gateway' => $order->get_payment_method(), 'transaction_id' => $order->get_transaction_id(), 'shipping_country' => $order->get_shipping_country()];
            $checks[$key . ':commande_sans_paiement'] = !$order->get_date_paid() && !$order->get_transaction_id()
                && $order->get_payment_method() === '' && (float) $order->get_total() === 0.0 && $order->get_status() === 'on-hold';
            $checks[$key . ':produit_commande'] = $order->get_item_count() === 1;
        }
        foreach ($subs as $sub) {
            $expected = match ($row['native']) { 'grace', 'suspended' => 'on-hold', default => $row['native'] };
            $entry['subscriptions'][] = ['id' => $sub->get_id(), 'parent_id' => $sub->get_parent_id(), 'customer_id' => $sub->get_customer_id(),
                'status' => $sub->get_status(), 'start' => $sub->get_date('start'), 'end' => $sub->get_date('end'),
                'next_payment' => $sub->get_date('next_payment'), 'manual' => $sub->is_manual(), 'payment_count' => $sub->get_payment_count(),
                'grace_start' => $sub->get_meta('_imagine_acces_grace_debut'), 'grace_end' => $sub->get_meta('_imagine_acces_grace_fin')];
            $checks[$key . ':etat_abonnement'] = $sub->get_status() === $expected;
            $checks[$key . ':aucun_paiement_automatique'] = $sub->is_manual() && !$sub->get_payment_method() && !$sub->get_transaction_id()
                && !$sub->get_date_paid() && $sub->get_payment_count() === 0;
            $checks[$key . ':parent_natif'] = isset($orders[0]) && $sub->get_parent_id() === $orders[0]->get_id();
            $linked = wc_memberships_get_memberships_from_subscription($sub);
            $checks[$key . ':adhesion_lien_natif'] = count($linked) === 1 && $linked[0]->get_user_id() === $id;
            $checks[$key . ':produit_abonnement'] = $sub->get_item_count() === 1;
            $next = $sub->get_time('next_payment');
            $checks[$key . ':prochain_paiement'] = in_array($row['native'], ['expired', 'pending-cancel'], true) ? !$next : $next > time();
            if ($key === 'A-GRACE' || $key === 'A-SUSP') {
                $from = $sub->get_meta('_imagine_acces_grace_debut');
                $until = $sub->get_meta('_imagine_acces_grace_fin');
                $now = gmdate('Y-m-d H:i:s');
                $checks[$key . ':fenetre_grace'] = $key === 'A-GRACE' ? $from <= $now && $now < $until : $from < $until && $until < $now;
            }
            if ($key === 'A-ECHEANCE') {
                $checks[$key . ':terme_30_jours'] = abs($sub->get_time('end') - (time() + 30 * DAY_IN_SECONDS)) < 300;
            }
            if ($key === 'A-PAPIER') {
                $checks[$key . ':echeance_ce_mois'] = gmdate('Y-m', $next) === gmdate('Y-m');
            }
        }
        foreach ($members as $member) {
            $entry['memberships'][] = ['id' => $member->get_id(), 'user_id' => $member->get_user_id(), 'plan_id' => $member->get_plan_id(),
                'status' => $member->get_status(), 'order_id' => $member->get_order_id(),
                'start' => $member->get_start_date(), 'end' => $member->get_end_date('mysql', false)];
            $expected = match ($row['native'] ?? '') { 'grace', 'suspended' => 'paused', 'pending' => 'pending', 'expired' => 'expired', default => 'active' };
            $checks[$key . ':etat_adhesion'] = $member->get_status() === $expected;
            $checks[$key . ':plan_adhesion'] = $member->get_plan_id() === $fixture['plan'];
            if ($key === 'P-SOL-OK') {
                $checks[$key . ':fin_45_jours'] = abs(strtotime($member->get_end_date('mysql', false) . ' UTC') - (time() + 45 * DAY_IN_SECONDS)) < 300;
            }
        }
        if ($key === 'A-ETRANGER') {
            $checks[$key . ':port_natif_fictif'] = $orders[0]->get_shipping_country() === 'FR' && count($orders[0]->get_items('shipping')) === 1;
        }
        if ($key === 'E-REDAC') {
            $checks[$key . ':contenus_calendrier'] = user_can($id, 'edit_posts') && user_can($id, get_post_type_object('imagine_numero')->cap->edit_posts)
                && !user_can($id, 'manage_options');
        }
        if ($key === 'E-ABO') { $checks[$key . ':gestion_commandes'] = user_can($id, 'edit_shop_orders') && !user_can($id, 'manage_options'); }
        $proof[$key] = $entry;
    }
    $checks['aucun_compte_visiteur_robot'] = !get_user_by('login', 'v-robot');
    $checks['numero_entreprise_coherent_non_atteste'] = \Imagine\Pilotage\Entreprise\NumeroEntreprise::depuisSaisie('0000000097')->estValide();
    $checks['mail_coupe'] = wp_mail('c09@example.org', 'Fictif C09', 'Fictif') === false;
    $checks['http_coupe'] = is_wp_error(wp_remote_get('https://example.org'));
    $checks['passerelles_coupees'] = WC()->payment_gateways()->get_available_payment_gateways() === [];
    $checks['catalogue_plan_droits'] = (get_option('imagine_acces_plans')[$fixture['plan']] ?? null) === 'abonnement';
    $ownedUsers = get_users(['meta_key' => '_imagine_c09_fixture', 'fields' => 'ID']);
    $checks['inventaire_total_27_comptes'] = count($ownedUsers) === 27;
    foreach (['shop_order' => 13, 'shop_subscription' => 12] as $type => $expected) {
        $objects = wc_get_orders(['type' => $type, 'status' => array_keys($type === 'shop_subscription' ? wcs_get_subscription_statuses() : wc_get_order_statuses()),
            'limit' => -1, 'meta_query' => [['key' => '_imagine_c09_fixture', 'compare' => 'EXISTS']]]);
        $checks['inventaire_total_' . $type] = count($objects) === $expected;
    }
    $allMembers = get_posts(['post_type' => 'wc_user_membership', 'post_status' => array_keys(get_post_stati()),
        'posts_per_page' => -1, 'meta_key' => '_imagine_c09_fixture']);
    $checks['inventaire_total_14_adhesions'] = count($allMembers) === 14;
    $product = wc_get_product($fixture['product']);
    $checks['produit_natif_subscription_prive_zero'] = $product instanceof \WC_Product_Subscription
        && $product->get_status() === 'private' && $product->get_catalog_visibility() === 'hidden' && (float) $product->get_price() === 0.0;
    foreach ($fixture['subscriptions'] as $key => $id) {
        $sub = wcs_get_subscription($id);
        $scheduled = as_next_scheduled_action('woocommerce_scheduled_subscription_payment', ['subscription_id' => $id]);
        $checks[$key . ':action_native_planifiee_ou_absente_selon_statut'] = $sub->has_status('active')
            ? $scheduled === $sub->get_time('next_payment') : $scheduled === false;
        $checks[$key . ':periodicite_reinitialisee'] = $sub->get_billing_period() === 'year' && (int) $sub->get_billing_interval() === 1;
        $proof[$key]['subscriptions'][0]['scheduled_payment_action'] = $scheduled;
    }
    wp_set_current_user(0);
}
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['total' => count($checks), 'failures' => $failures, 'checks' => $checks, 'proof' => $proof,
    'fixture' => $fixture], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
if ($failures) { \WP_CLI::halt(1); }
