<?php
/** C09 : vrais objets natifs, zéro paiement, propriété stricte, remise à l'état initial. */
declare(strict_types=1);
namespace Imagine\Demo\C09;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || basename(dirname(WP_CONTENT_DIR)) === 'production') {
    throw new \RuntimeException('C09 refuse cette cible.');
}
if (!is_file(WPMU_PLUGIN_DIR . '/imagine-demo-offline.php')
    || wp_mail('c09@example.org', 'C09', 'Fixture') !== false
    || !is_wp_error(wp_remote_get('https://example.org'))
    || WC()->payment_gateways()->get_available_payment_gateways() !== []) {
    throw new \RuntimeException('Garde hors ligne C09 absente.');
}
$secret = json_decode(file_get_contents('/var/www/.imagine-demo/seed-secret.json'), true, 512, JSON_THROW_ON_ERROR);
$rows = json_decode(file_get_contents(WP_CONTENT_DIR . '/imagine-demo-build/c09-profils.json'), true, 512, JSON_THROW_ON_ERROR);
$now = new \DateTimeImmutable('now', new \DateTimeZone('UTC'));
$date = static fn (string $offset): string => $now->modify($offset)->format('Y-m-d H:i:s');
$owned = '_imagine_c09_fixture';
// Prévol complet avant mutation : jamais adopter un compte/plan/produit étranger.
foreach ($rows as $row) {
    if (!$row['compte']) { continue; }
    $login = strtolower($row['code']);
    if (!isset($secret['c09_accounts'][$row['code']]['password'])) { throw new \RuntimeException('Secret C09 incomplet.'); }
    $user = get_user_by('login', $login);
    if ($user && get_user_meta($user->ID, $owned, true) !== $row['code']) {
        throw new \RuntimeException('Collision de compte C09 : ' . $row['code']);
    }
    $email = get_user_by('email', $login . '@example.org');
    if ($email && (!$user || $email->ID !== $user->ID)) { throw new \RuntimeException('Collision email C09.'); }
    if ($user) {
        foreach (array_merge(wc_get_orders(['customer_id' => $user->ID, 'type' => 'shop_order', 'limit' => -1]),
            array_values(wcs_get_users_subscriptions($user->ID))) as $object) {
            if ($object->get_meta($owned) !== $row['code']) { throw new \RuntimeException('Objet commercial étranger sur un profil C09 ; refus.'); }
        }
        foreach (wc_memberships_get_user_memberships($user->ID, ['status' => 'any']) ?? [] as $member) {
            if (get_post_meta($member->get_id(), $owned, true) !== $row['code']) { throw new \RuntimeException('Adhésion étrangère sur profil C09 ; refus.'); }
        }
    }
}
foreach (['wc_membership_plan' => 'c09-lecture-fictive', 'product' => 'c09-abonnement-fictif'] as $type => $slug) {
    $existing = get_page_by_path($slug, OBJECT, $type);
    if ($existing && get_post_meta($existing->ID, $owned, true) !== 'shared') { throw new \RuntimeException('Collision catalogue C09.'); }
}
$planPost = get_page_by_path('c09-lecture-fictive', OBJECT, 'wc_membership_plan');
$planId = wp_insert_post(['ID' => $planPost->ID ?? 0, 'post_type' => 'wc_membership_plan', 'post_status' => 'publish',
    'post_title' => 'C09 — Lecture fictive, hors ligne', 'post_name' => 'c09-lecture-fictive',
    'meta_input' => [$owned => 'shared', '_access_method' => 'manual-only']], true);
if (is_wp_error($planId)) { throw new \RuntimeException('Plan natif C09 impossible.'); }
$plans = get_option('imagine_acces_plans', []);
$plans[$planId] = 'abonnement';
update_option('imagine_acces_plans', $plans);
$productPost = get_page_by_path('c09-abonnement-fictif', OBJECT, 'product');
$product = new \WC_Product_Subscription($productPost->ID ?? 0);
$product->set_name('C09 — Abonnement de fixture sans paiement (pas une offre)');
$product->set_slug('c09-abonnement-fictif');
$product->set_status('private');
$product->set_catalog_visibility('hidden');
$product->set_virtual(true);
$product->set_regular_price('0');
$product->set_price('0');
$product->set_tax_status('none');
$product->update_meta_data($owned, 'shared');
$product->update_meta_data('_subscription_price', '0');
$product->update_meta_data('_subscription_period', 'year');
$product->update_meta_data('_subscription_period_interval', '1');
$product->update_meta_data('_subscription_length', '1');
$product->save();
// Sélection stable ; seules les copies explicitement possédées sont supprimées.
$one = static function (array $objects) {
    usort($objects, static fn ($a, $b) => $a->get_id() <=> $b->get_id());
    $first = array_shift($objects);
    foreach ($objects as $extra) { $extra->delete(true); }
    return $first;
};
$manifest = ['plan' => (int) $planId, 'product' => $product->get_id(), 'users' => [], 'orders' => [], 'subscriptions' => [], 'memberships' => []];
foreach ($rows as $row) {
    if (!$row['compte']) { continue; }
    $key = $row['code'];
    $login = strtolower($key);
    $account = $secret['c09_accounts'][$key];
    $user = get_user_by('login', $login);
    $data = ['user_login' => $login, 'user_email' => $login . '@example.org',
        'user_pass' => $account['password'], 'display_name' => 'Personnage Fictif C09 ' . $key,
        'first_name' => 'Personnage Fictif', 'last_name' => $key, 'user_url' => '',
        'description' => 'Compte de démonstration fictif C09, aucune personne réelle.',
        'role' => $row['role'] ?? 'customer', 'meta_input' => [$owned => $key]];
    if ($user) { $data['ID'] = $user->ID; $id = wp_update_user($data); } else { $id = wp_insert_user($data); }
    if (is_wp_error($id)) { throw new \RuntimeException('Compte C09 non créé : ' . $key); }
    $user = new \WP_User($id);
    $user->remove_all_caps();
    $user->set_role($row['role'] ?? 'customer');
    \WP_Session_Tokens::get_instance($id)->destroy_all();
    if (!wp_check_password($account['password'], get_userdata($id)->user_pass, $id)) { wp_set_password($account['password'], $id); }
    $customer = new \WC_Customer($id);
    $address = ['first_name' => 'Personnage Fictif', 'last_name' => $key, 'company' => $key === 'P-PRO' ? 'Entreprise Fictive C09' : '',
        'address_1' => '1 rue Imaginaire', 'address_2' => '', 'city' => 'Ville Fictive', 'state' => '',
        'postcode' => $key === 'A-ETRANGER' ? '75000' : '1000', 'country' => $key === 'A-ETRANGER' ? 'FR' : 'BE'];
    foreach ($address as $field => $value) {
        $customer->{'set_billing_' . $field}($value);
        $customer->{'set_shipping_' . $field}($value);
    }
    $customer->set_billing_email($login . '@example.org');
    $customer->set_billing_phone('');
    $customer->save();
    $manifest['users'][$key] = $id;
    // Revenir aussi à l'absence initiale : ne conserver aucun objet C09 additionnel.
    // Le prévol ci-dessus a déjà refusé tout objet non possédé.
    if (!isset($row['native'])) {
        foreach (wcs_get_users_subscriptions($id) as $extra) { $extra->delete(true); }
    }
    if (!isset($row['native']) && !isset($row['membership'])) {
        foreach (wc_memberships_get_user_memberships($id, ['status' => 'any']) ?? [] as $extra) { wp_delete_post($extra->get_id(), true); }
    }
    if (!isset($row['native']) && empty($row['order_only'])) {
        foreach (wc_get_orders(['customer_id' => $id, 'type' => 'shop_order', 'limit' => -1]) as $extra) { $extra->delete(true); }
    }
    $order = null;
    if (isset($row['native']) || !empty($row['order_only'])) {
        $order = $one(wc_get_orders(['customer_id' => $id, 'type' => 'shop_order', 'limit' => -1]));
        if (!$order) { $order = wc_create_order(['customer_id' => $id, 'created_via' => 'admin', 'status' => 'pending']); }
        if (is_wp_error($order)) { throw new \RuntimeException('Commande C09 impossible.'); }
        $order->set_customer_id($id);
        $order->set_created_via('admin');
        // last_payment est un alias historique WCS de dernière création de commande,
        // même sans date_paid : dater la fixture avant son terme expiré, sans paiement.
        $order->set_date_created($now->modify('-335 days')->getTimestamp());
        $order->set_address($address + ['email' => $login . '@example.org', 'phone' => ''], 'billing');
        $order->set_address($address, 'shipping');
        $order->set_currency('EUR');
        $order->set_payment_method('');
        $order->set_payment_method_title('Aucun paiement — fixture administrative C09');
        $order->set_transaction_id('');
        $order->set_date_paid(null);
        $order->set_date_completed(null);
        $order->set_customer_note('FICTIF C09 : aucun règlement, mandat ou transaction.');
        $order->update_meta_data($owned, $key);
        $order->remove_order_items();
        if (!empty($row['order_only'])) {
            $item = new \WC_Order_Item_Product();
            $item->set_name('Numéro fictif ' . get_option('imagine_demo_manifest')['demo-2026-t1'] . ' — acquisition non validée');
            $item->set_quantity(1);
            $item->set_total('0');
            $item->set_subtotal('0');
            $order->add_item($item);
        } else {
            $order->add_product($product, 1, ['subtotal' => 0, 'total' => 0]);
        }
        if ($key === 'A-ETRANGER') {
            $shipping = new \WC_Order_Item_Shipping();
            $shipping->set_method_title('Port hors Belgique — montant de fixture, tarif non arrêté');
            $shipping->set_method_id('imagine_c09_fixture');
            $shipping->set_total('0');
            $order->add_item($shipping);
        }
        $order->calculate_totals(false);
        $order->set_status('on-hold');
        $order->save();
        $manifest['orders'][$key] = $order->get_id();
    }
    $sub = null;
    if (isset($row['native'])) {
        $sub = $one(array_values(wcs_get_users_subscriptions($id)));
        if (!$sub) { $sub = wcs_create_subscription(['customer_id' => $id, 'order_id' => $order->get_id(), 'status' => 'pending',
            'start_date' => $date('-365 days'), 'billing_period' => 'year', 'billing_interval' => 1]); }
        if (is_wp_error($sub)) { throw new \RuntimeException('Souscription C09 impossible.'); }
        $sub->set_customer_id($id);
        $sub->set_parent_id($order->get_id());
        $sub->set_billing_period('year');
        $sub->set_billing_interval(1);
        $sub->set_requires_manual_renewal(true);
        $sub->set_payment_method('');
        $sub->set_payment_method_title('Fixture C09 — renouvellement manuel de sécurité');
        $sub->set_transaction_id('');
        $sub->set_date_paid(null);
        $sub->set_date_completed(null);
        $sub->set_address($address + ['email' => $login . '@example.org', 'phone' => ''], 'billing');
        $sub->set_address($address, 'shipping');
        $sub->update_meta_data($owned, $key);
        $sub->remove_order_items();
        $sub->add_product($product, 1, ['subtotal' => 0, 'total' => 0]);
        $sub->calculate_totals(false);
        $start = $date('-335 days');
        $end = $date('+365 days');
        $next = $date('+30 days');
        if ($key === 'A-ECHEANCE') { $end = $date('+30 days'); $next = $date('+29 days'); }
        if ($row['native'] === 'pending-cancel') { $end = $date('+30 days'); $next = 0; }
        if ($row['native'] === 'expired') { $end = $date('-1 day'); $next = 0; }
        if ($key === 'A-PAPIER') {
            $last = $now->modify('last day of this month')->setTime(23, 59, 59);
            $next = min($now->modify('+1 hour'), $last)->format('Y-m-d H:i:s');
        }
        $sub->update_dates(['start' => $start, 'trial_end' => 0, 'next_payment' => $next, 'end' => $end, 'cancelled' => 0], 'gmt');
        $sub->update_meta_data('_imagine_acces_grace_debut', $row['native'] === 'grace' ? $date('-1 day') : ($row['native'] === 'suspended' ? $date('-4 days') : ''));
        $sub->update_meta_data('_imagine_acces_grace_fin', $row['native'] === 'grace' ? $date('+2 days') : ($row['native'] === 'suspended' ? $date('-1 day') : ''));
        $sub->save();
        // Le statut administratif ne signifie pas paiement. Aucun payment_complete().
        $sub->set_status(match ($row['native']) { 'grace', 'suspended' => 'on-hold', default => $row['native'] });
        $sub->save();
        $manifest['subscriptions'][$key] = $sub->get_id();
    }
    if (isset($row['native']) || isset($row['membership'])) {
        $members = wc_memberships_get_user_memberships($id, ['status' => 'any']) ?? [];
        usort($members, static fn ($a, $b) => $a->get_id() <=> $b->get_id());
        $member = array_shift($members);
        foreach ($members as $extra) { wp_delete_post($extra->get_id(), true); }
        if (!$member) { $member = wc_memberships_create_user_membership(['plan_id' => $planId, 'user_id' => $id,
            'order_id' => $order ? $order->get_id() : 0, 'product_id' => $order ? $product->get_id() : 0]); }
        if (is_wp_error($member)) { throw new \RuntimeException('Adhésion C09 impossible.'); }
        $member->set_order_id($order ? $order->get_id() : 0);
        $member->set_product_id($order ? $product->get_id() : 0);
        $member->set_start_date($date('-335 days'));
        $member->set_end_date($key === 'P-SOL-OK' ? $date('+45 days') : ($sub ? $sub->get_date('end') : $date('+365 days')));
        update_post_meta($member->get_id(), $owned, $key);
        if ($sub) { update_post_meta($member->get_id(), '_subscription_id', $sub->get_id()); }
        else { delete_post_meta($member->get_id(), '_subscription_id'); }
        $member->update_status(match ($row['native'] ?? '') { 'grace', 'suspended' => 'paused', 'pending' => 'pending', 'expired' => 'expired', default => 'active' });
        $manifest['memberships'][$key] = $member->get_id();
    }
}
update_option('imagine_c09_fixture', $manifest);
echo wp_json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
