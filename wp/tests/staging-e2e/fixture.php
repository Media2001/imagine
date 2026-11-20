<?php

declare(strict_types=1);

// Real WordPress + WooCommerce APIs. All identities, addresses and traps are invented.
namespace Imagine\E2E;

if (!defined('ABSPATH') || !class_exists('WooCommerce') || wp_get_environment_type() !== 'staging') {
    throw new \RuntimeException('Synthetic fixture requires its isolated staging WordPress');
}
add_filter('pre_wp_mail', '__return_true', PHP_INT_MAX); // Seed-process only; not installed as an MU-plugin.
add_filter('woocommerce_allow_tracking', '__return_false');

$product = new \WC_Product_Simple();
$product->set_name('Magazine entièrement fictif E2E');
$product->set_regular_price('12.50');
$product->set_virtual(true);
$product->set_status('publish');
$productId = $product->save();
$ids = [1];
wp_update_user(['ID' => 1, 'display_name' => 'Administrateur inventé E2E']);
for ($i = 2; $i <= 30; ++$i) {
    $id = wp_insert_user([
        'user_login' => sprintf('fictif-%02d', $i),
        'user_email' => sprintf('fictif-%02d@example.org', $i),
        'user_pass' => wp_generate_password(40, true, true),
        'role' => 'customer',
        'display_name' => sprintf('Personnage inventé %02d', $i),
        'first_name' => sprintf('PrénomFictif%02d', $i),
        'last_name' => sprintf('NomFictif%02d', $i),
    ]);
    if (is_wp_error($id)) {
        throw new \RuntimeException($id->get_error_message());
    }
    $ids[] = $id;
    foreach (['billing', 'shipping'] as $type) {
        foreach (['first_name' => 'PrénomFictif', 'last_name' => sprintf('NomFictif%02d', $i),
            'company' => 'Entreprise imaginaire E2E', 'address_1' => 'Voie totalement inventée ' . $i,
            'address_2' => 'Bâtiment imaginaire', 'city' => 'Ville inventée', 'postcode' => '00000',
            'country' => ['BE', 'FR', 'DE'][$i % 3], 'state' => '',
            'phone' => '+00000000' . $i, 'email' => sprintf('fictif-%02d@example.org', $i)] as $key => $value) {
            update_user_meta($id, $type . '_' . $key, $value);
        }
    }
    update_user_meta($id, 'billing_company_number', 'SYNTHETIC-NOT-A-REGISTRATION-' . $i);
    update_user_meta($id, 'session_tokens', ['synthetic-session-' . $i => ['expiration' => 1893456000, 'ip' => '192.0.2.123', 'ua' => 'Synthetic fixture only']]);
}
$orders = [];
for ($i = 1; $i <= 30; ++$i) {
    $order = wc_create_order(['customer_id' => $i === 30 ? 0 : $ids[$i - 1]]);
    $order->add_product($product, ($i % 3) + 1);
    $order->set_currency('EUR');
    $order->set_date_created(sprintf('2026-10-%02d 12:00:00', ($i % 28) + 1));
    $order->set_payment_method(['bacs', 'stripe', 'paypal'][$i % 3]);
    $order->set_payment_method_title('Passerelle fictive sans connexion');
    $address = ['first_name' => 'PrénomFictif', 'last_name' => 'NomFictif' . $i,
        'company' => 'Entreprise imaginaire E2E', 'address_1' => 'Voie totalement inventée ' . $i,
        'address_2' => 'Bâtiment imaginaire', 'city' => 'Ville inventée', 'postcode' => '00000',
        'country' => ['BE', 'FR', 'DE'][$i % 3], 'state' => '',
        'email' => sprintf('commande-%02d@example.org', $i), 'phone' => '+00000000' . $i];
    $order->set_address($address, 'billing');
    $order->set_address($address, 'shipping');
    $order->set_status(['pending', 'on-hold', 'completed'][$i % 3]);
    $order->set_customer_ip_address('192.0.2.123');
    $order->set_customer_user_agent('Synthetic fixture only');
    $order->calculate_totals();
    $order->save();
    $order->add_order_note('Note entièrement inventée E2E, sans destinataire réel.');
    $orders[] = $order->get_id();
}
// Unknown form CPTs belong to an explicit refusal test, not the clean positive fixture.
update_option('blog_public', '0');
update_option('woocommerce_allow_tracking', 'no');
update_option('imagine_e2e_fixture', ['users' => $ids, 'orders' => $orders, 'product' => $productId]);
if (count($ids) !== 30 || count($orders) !== 30) {
    throw new \RuntimeException('Fixture count mismatch');
}
echo "E2E_FIXTURE_CREATED users=30 orders=30\n";
