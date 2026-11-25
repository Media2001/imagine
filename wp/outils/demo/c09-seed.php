<?php
/** C09 : vrais objets natifs, zéro paiement, propriété stricte, remise à l'état initial. */
declare(strict_types=1);
namespace Imagine\Demo\C09;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085'
    || basename(dirname(WP_CONTENT_DIR)) === 'production') {
    throw new \RuntimeException('C09 refuse cette cible.');
}
// Inspection passive : jamais wp_mail()/wp_remote_*() pour prouver une interdiction.
$mu = realpath(WPMU_PLUGIN_DIR . '/imagine-demo-offline.php');
$loaded = $mu && in_array($mu, array_map('realpath', get_included_files()), true);
$intercepted = $loaded;
foreach (['pre_wp_mail', 'pre_http_request', 'woocommerce_available_payment_gateways'] as $hook) {
    $nativeGuard = false;
    if (has_filter($hook)) {
        foreach (($GLOBALS['wp_filter'][$hook]->callbacks[PHP_INT_MAX] ?? []) as $callback) {
            if ($callback['function'] instanceof \Closure
                && realpath((new \ReflectionFunction($callback['function']))->getFileName()) === $mu) {
                $nativeGuard = true;
            }
        }
    }
    $intercepted = $intercepted && $nativeGuard;
}
if (!$intercepted) { throw new \RuntimeException('Garde hors ligne C09 absente.'); }
// Exercer seulement les filtres, jamais leurs transports.
$mailClosed = apply_filters('pre_wp_mail', null, ['to' => 'c09@example.org', 'subject' => 'Sentinelle passive', 'message' => '', 'headers' => [], 'attachments' => []]);
$httpClosed = apply_filters('pre_http_request', false, [], 'https://example.org');
if ($mailClosed !== false || !is_wp_error($httpClosed) || $httpClosed->get_error_code() !== 'imagine_demo_offline'
    || apply_filters('woocommerce_available_payment_gateways', []) !== []) {
    throw new \RuntimeException('Garde hors ligne C09 absente.');
}
$secret = json_decode(file_get_contents('/var/www/.imagine-demo/seed-secret.json'), true, 512, JSON_THROW_ON_ERROR);
$rows = json_decode(file_get_contents(WP_CONTENT_DIR . '/imagine-demo-build/c09-profils.json'), true, 512, JSON_THROW_ON_ERROR);
require_once __DIR__ . '/c09-calendar.php';
$now = now();
$date = static fn (string $offset): string => $now->modify($offset)->format('Y-m-d H:i:s');
$owned = '_imagine_c09_fixture';
$tariffs = [];
// Données synthétiques autorisées par la correction : jamais des prix Imagine.
foreach (['normal' => 120, 'solidaire' => 60, 'soutien' => 240] as $tarif => $annual) {
    foreach ([1, 4] as $times) {
        $tariffs[$tarif . '-' . $times] = ['price' => (string) ($annual / $times),
            'period' => $times === 1 ? 'year' : 'month', 'interval' => $times === 1 ? 1 : 3,
            'length' => $times === 1 ? 1 : 12];
    }
}
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
$roleName = 'imagine_referent_abonnements';
if (get_role($roleName) && get_option('imagine_c09_role_owned') !== 'c09') {
    throw new \RuntimeException('Collision rôle C09.');
}
foreach ($tariffs as $key => $spec) {
    $existing = get_page_by_path('c09-tarif-fictif-' . $key, OBJECT, 'product');
    if ($existing && get_post_meta($existing->ID, $owned, true) !== 'shared') { throw new \RuntimeException('Collision tarif C09.'); }
}
// Rôle natif persistant : seulement commandes et opérations §3.13, jamais shop_manager.
$caps = array_fill_keys(['read', 'edit_shop_orders', 'edit_others_shop_orders', 'read_private_shop_orders',
    'edit_private_shop_orders', 'edit_published_shop_orders', 'publish_shop_orders',
    'imagine_creer_compte_client', 'imagine_gerer_echeances', 'imagine_traiter_justificatifs',
    'imagine_exporter_liste_envoi', 'imagine_extraire_abonnes'], true);
if (!get_role($roleName)) { add_role($roleName, 'Référent abonnements', $caps); }
$role = get_role($roleName);
foreach (array_keys($role->capabilities) as $cap) { if (!isset($caps[$cap])) { $role->remove_cap($cap); } }
foreach ($caps as $cap => $value) { $role->add_cap($cap, $value); }
update_option('imagine_c09_role_owned', 'c09');
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
$defaultProduct = $product;
$tariffProducts = [];
foreach ($tariffs as $key => $spec) {
    $existing = get_page_by_path('c09-tarif-fictif-' . $key, OBJECT, 'product');
    $p = new \WC_Product_Subscription($existing->ID ?? 0);
    $p->set_name('C09 FICTIF — ' . $key . ' — pas une offre Imagine');
    $p->set_slug('c09-tarif-fictif-' . $key);
    $p->set_status('private'); $p->set_catalog_visibility('hidden'); $p->set_virtual(true);
    $p->set_regular_price($spec['price']); $p->set_price($spec['price']); $p->set_tax_status('none');
    $p->update_meta_data($owned, 'shared');
    $p->update_meta_data('_subscription_price', $spec['price']);
    $p->update_meta_data('_subscription_period', $spec['period']);
    $p->update_meta_data('_subscription_period_interval', (string) $spec['interval']);
    $p->update_meta_data('_subscription_length', (string) $spec['length']);
    $p->save();
    $tariffProducts[$key] = $p;
}
// Sélection stable ; seules les copies explicitement possédées sont supprimées.
$one = static function (array $objects) {
    usort($objects, static fn ($a, $b) => $a->get_id() <=> $b->get_id());
    $first = array_shift($objects);
    foreach ($objects as $extra) { $extra->delete(true); }
    return $first;
};
$manifest = ['plan' => (int) $planId, 'product' => $product->get_id(), 'users' => [], 'orders' => [], 'subscriptions' => [], 'memberships' => []];
$manifest['tariffs'] = array_map(static fn ($p) => $p->get_id(), $tariffProducts);
foreach ($rows as $row) {
    if (!$row['compte']) { continue; }
    $key = $row['code'];
    $product = isset($row['tarif']) ? $tariffProducts[$row['tarif']] : $defaultProduct;
    $fixtureAmount = isset($row['tarif']) ? $product->get_price() : '0';
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
    if (($row['decouverte'] ?? null) === 'C12') {
        require_once __DIR__ . '/c12-profils.php';
        \Imagine\Demo\C12\profil((int) $id, $key, true);
    }
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
        $parentOrders = array_filter(wc_get_orders(['customer_id' => $id, 'type' => 'shop_order', 'limit' => -1]),
            static fn ($o) => !$o->get_meta('_subscription_renewal'));
        $order = $one(array_values($parentOrders));
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
            $order->add_product($product, 1, ['subtotal' => $fixtureAmount, 'total' => $fixtureAmount]);
        }
        if ($key === 'A-ETRANGER') {
            $shipping = new \WC_Order_Item_Shipping();
            $shipping->set_method_title('Port hors Belgique — montant de fixture, tarif non arrêté');
            $shipping->set_method_id('imagine_c09_fixture');
            $shipping->set_total('0');
            $order->add_item($shipping);
        }
        $order->calculate_totals(false);
        $paidInitial = in_array($key, ['A-CARTE', 'A-PAYPAL', 'A-ETRANGER', 'A-SANSMAIL', 'A-ECHEANCE', 'A-NONRENOUV', 'A-SEPA4', 'A-PAPIER'], true);
        $order->update_meta_data('imagine_demo_fictif', '1');
        $order->set_payment_method_title('Paiement fictif de démonstration');
        $order->set_customer_note('FICTIF C09 : état natif de démonstration, aucun règlement, mandat ou transaction réel.');
        $order->set_status($paidInitial ? 'processing' : 'on-hold');
        $order->set_date_paid($paidInitial ? $now->modify('-335 days')->getTimestamp() : null);
        $order->save();
        if ($key === 'P-NUMERO') {
            require_once __DIR__ . '/c14-profil.php';
            \Imagine\Demo\C14\profil((int) $id, $order);
        }
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
        $sub->set_billing_period(isset($row['tarif']) ? $tariffs[$row['tarif']]['period'] : 'year');
        $sub->set_billing_interval(isset($row['tarif']) ? $tariffs[$row['tarif']]['interval'] : 1);
        $sub->set_requires_manual_renewal(true);
        $sub->set_payment_method('');
        $sub->set_payment_method_title('Paiement fictif de démonstration');
        $sub->update_meta_data('imagine_demo_fictif', '1');
        $sub->set_transaction_id('');
        $sub->set_date_paid(null);
        $sub->set_date_completed(null);
        $sub->set_address($address + ['email' => $login . '@example.org', 'phone' => ''], 'billing');
        $sub->set_address($address, 'shipping');
        $sub->update_meta_data($owned, $key);
        $sub->remove_order_items();
        $sub->add_product($product, 1, ['subtotal' => $fixtureAmount, 'total' => $fixtureAmount]);
        $sub->calculate_totals(false);
        $start = $paidInitial ? $date($key === 'A-SEPA4' ? '-180 days' : '-90 days') : $date('-335 days');
        $end = $date('+365 days');
        $next = $date('+30 days');
        if ($key === 'A-ECHEANCE') { $end = $date('+30 days'); $next = $date('+29 days'); }
        if ($row['native'] === 'pending-cancel') { $end = $date('+30 days'); $next = 0; }
        if ($row['native'] === 'expired') { $end = $date('-1 day'); $next = 0; }
        if ($key === 'A-PAPIER') {
            $next = papierDue($now);
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
        // L'API Memberships accepte aussi un ID existant et remet post_parent/plan.
        $member = wc_memberships_create_user_membership(['user_membership_id' => $member ? $member->get_id() : 0,
            'plan_id' => $planId, 'user_id' => $id,
            'order_id' => $order ? $order->get_id() : 0, 'product_id' => $order ? $product->get_id() : 0]);
        if (is_wp_error($member)) { throw new \RuntimeException('Adhésion C09 impossible.'); }
        $member->set_order_id($order ? $order->get_id() : 0);
        $member->set_product_id($order ? $product->get_id() : 0);
        $member->set_start_date($sub ? $sub->get_date('start') : $date('-335 days'));
        $member->set_end_date($key === 'P-SOL-OK' ? $date('+45 days') : ($sub ? $sub->get_date('end') : $date('+365 days')));
        update_post_meta($member->get_id(), $owned, $key);
        if ($sub) { update_post_meta($member->get_id(), '_subscription_id', $sub->get_id()); }
        else { delete_post_meta($member->get_id(), '_subscription_id'); }
        $member->update_status(match ($row['native'] ?? '') { 'grace', 'suspended' => 'paused', 'pending' => 'pending', 'expired' => 'expired', default => 'active' });
        $manifest['memberships'][$key] = $member->get_id();
    }
}
$manifest['renewals'] = [];
foreach ($manifest['subscriptions'] as $key => $id) {
    $sub = wcs_get_subscription($id);
    $related = array_map('wc_get_order', array_values($sub->get_related_orders('ids', 'renewal')));
    // Le prévol garantit la propriété C09 avant tout retrait de doublon.
    foreach ($related as $relatedOrder) {
        if (!$relatedOrder || $relatedOrder->get_meta($owned) !== $key) {
            throw new \RuntimeException('Renouvellement étranger C09 ; refus.');
        }
    }
    if (!in_array($key, ['A-SEPA4', 'A-GRACE', 'A-SUSP'], true)) {
        foreach ($related as $extra) { $extra->delete(true); }
        continue;
    }
    $dates = ['start' => $sub->get_date('start'), 'trial_end' => 0, 'end' => $sub->get_date('end'),
        'next_payment' => $sub->get_date('next_payment'), 'cancelled' => 0];
    $renewal = $one($related);
    if (!$renewal) { $renewal = wcs_create_renewal_order($sub); }
    if (is_wp_error($renewal)) { throw new \RuntimeException('Renouvellement natif C09 impossible.'); }
    $renewal->set_customer_id($sub->get_customer_id());
    $renewal->set_created_via('admin');
    $renewal->set_currency('EUR');
    $renewal->set_payment_method('');
    $renewal->set_payment_method_title('Paiement fictif de démonstration');
    $renewal->set_transaction_id('');
    $renewal->set_date_paid(null);
    $renewal->set_date_completed(null);
    $renewal->set_customer_note('FICTIF C09 : état natif autorisé de démonstration, aucun débit ou rejet bancaire réel.');
    $renewal->update_meta_data($owned, $key);
    $renewal->update_meta_data('imagine_demo_fictif', '1');
    $renewal->set_address($sub->get_address('shipping'), 'shipping');
    $renewal->set_address($sub->get_address('billing'), 'billing');
    $renewal->remove_order_items();
    foreach ($sub->get_items() as $item) {
        $renewal->add_product($item->get_product(), 1, ['subtotal' => $item->get_subtotal(), 'total' => $item->get_total()]);
    }
    $renewal->calculate_totals(false);
    $when = $key === 'A-SEPA4' ? $now->modify('-30 days')->getTimestamp()
        : strtotime($sub->get_meta('_imagine_acces_grace_debut') . ' UTC');
    $renewal->set_date_created($when);
    $renewal->set_status($key === 'A-SEPA4' ? 'processing' : 'failed');
    $renewal->save();
    $renewal = wc_get_order($renewal->get_id());
    $renewal->set_date_paid($key === 'A-SEPA4' ? $when : null);
    $renewal->save();
    // Les transitions natives peuvent recalculer les dates ; rétablir la fixture décrite.
    $sub = wcs_get_subscription($id);
    $sub->update_dates($dates, 'gmt');
    $sub->set_requires_manual_renewal(true);
    $sub->set_status($key === 'A-SEPA4' ? 'active' : 'on-hold');
    $sub->save();
    $member = wc_memberships_get_user_membership($manifest['memberships'][$key]);
    $member->update_status($key === 'A-SEPA4' ? 'active' : 'paused');
    $manifest['renewals'][$key] = $renewal->get_id();
}
// Finaliser depuis une instance fraîche : les hooks natifs d'adhésion/statut peuvent
// relire la commande parente pendant le seed. Aucun payment_complete()/transport.
foreach (['A-CARTE', 'A-PAYPAL', 'A-ETRANGER', 'A-SANSMAIL', 'A-ECHEANCE', 'A-NONRENOUV', 'A-SEPA4', 'A-PAPIER'] as $key) {
    $paid = wc_get_order($manifest['orders'][$key]);
    $paid->set_date_created($now->modify($key === 'A-SEPA4' ? '-180 days' : '-90 days')->getTimestamp());
    $paid->set_date_paid($now->modify($key === 'A-SEPA4' ? '-180 days' : '-90 days')->getTimestamp());
    $paid->save();
}
// Marque lisible de chaque objet/ligne de cette fixture ; ne donne aucun droit.
foreach ($manifest['users'] as $id) { update_user_meta($id, 'imagine_demo_fictif', '1'); }
foreach ([$manifest['plan'], ...array_values($manifest['memberships'])] as $id) {
    update_post_meta($id, 'imagine_demo_fictif', '1');
}
foreach ([$manifest['product'], ...array_values($manifest['tariffs'])] as $id) {
    $p = wc_get_product($id); $p->update_meta_data('imagine_demo_fictif', '1'); $p->save();
}
foreach ([...array_values($manifest['orders']), ...array_values($manifest['subscriptions']), ...array_values($manifest['renewals'])] as $id) {
    $o = wc_get_order($id);
    $o->update_meta_data('imagine_demo_fictif', '1');
    $o->set_payment_method_title('Paiement fictif de démonstration');
    foreach (['line_item', 'shipping', 'fee'] as $type) {
        foreach ($o->get_items($type) as $item) { $item->update_meta_data('imagine_demo_fictif', '1'); $item->save(); }
    }
    $o->save();
}
update_option('imagine_c09_fixture', $manifest);
update_option('imagine_c09_seeded_at', $now->format('Y-m-d H:i:s'));
echo wp_json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
