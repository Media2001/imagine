<?php

declare(strict_types=1);

// Fixture-only writes, through native CRUD, before read-only photographs.
add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $old) {
    $old->delete(true);
}
update_option('woocommerce_default_country', 'BE');
update_option('woocommerce_checkout_company_field', 'optional');
update_option('woocommerce_checkout_address_2_field', 'optional');
update_option('woocommerce_checkout_phone_field', 'optional');
$address = ['first_name' => 'Abonne fictif', 'last_name' => 'Exemple invente', 'company' => '',
    'country' => 'BE', 'address_1' => 'A24_STREET_PRIVATE_CANARY', 'address_2' => '',
    'city' => 'Ville inventee', 'state' => '', 'postcode' => '1000', 'phone' => ''];
$states = ['active', 'pending', 'on-hold', 'pending-cancel', 'active'];
for ($i = 0; $i < 12; $i++) {
    $a = $address;
    if ($i === 5) {
        $a['country'] = 'FR';
        $a['postcode'] = '';
    } elseif ($i === 6) {
        $a = [];
    } elseif ($i === 7) {
        $a['country'] = '';
    } elseif ($i === 8) {
        $a['country'] = 'ZZ';
    } elseif ($i === 9) {
        $a['country'] = 'AE';
        $a['postcode'] = '';
    } elseif ($i === 10) {
        $a['country'] = 'US';
        $a['state'] = '';
    }
    $customer = new WC_Customer();
    $customer->set_username('a24-fictif-' . $i);
    $customer->set_email('a24-fictif-' . $i . '@example.org');
    $customer->set_password(bin2hex(random_bytes(24)));
    foreach ($a as $key => $value) {
        $method = 'set_shipping_' . $key;
        $customer->$method($value);
    }
    $customer->save();
    $s = wcs_create_subscription(['customer_id' => $customer->get_id(),
        'status' => 'pending', 'billing_period' => 'year', 'billing_interval' => 1,
        'start_date' => '2026-01-01 00:00:00']);
    if (is_wp_error($s)) {
        throw new RuntimeException('A24_FIXTURE_CREATE_FAILED');
    }
    if ($i === 1) {
        $a['address_1'] = strtolower($a['address_1']);
    } elseif ($i === 2) {
        $a['address_1'] .= ' ';
    }
    if ($i === 11) {
        $s->set_customer_id(0);
    }
    $s->set_address($a, 'shipping');
    $s->set_address($address, 'billing');
    // edit-context values are the oracle: WC sanitizers may trim at write time.
    if ($i === 2) {
        $a['address_1'] = ' ' . $address['address_1'];
        $customer->set_shipping_address_1($a['address_1']);
        $customer->save();
    }
    $s->save();
    if ($i === 2) {
        update_user_meta($customer->get_id(), 'shipping_address_1', ' ' . $address['address_1']);
    }
    $status = $states[$i] ?? 'active';
    if (!in_array($status, ['pending', 'active'], true)) {
        $s->update_status('active');
    }
    if ($status === 'pending-cancel') {
        $s->update_dates(['next_payment' => '2027-01-01 00:00:00']);
    }
    if ($status !== 'pending') {
        $s->update_status($status);
    }
}
// Excluded terminal statuses: do not contaminate live counts.
foreach (['cancelled', 'expired'] as $status) {
    $s = wcs_create_subscription(['customer_id' => $customer->get_id(), 'status' => 'pending', 'billing_period' => 'year', 'billing_interval' => 1,
        'start_date' => '2026-01-01 00:00:00']);
    $s->set_address([], 'shipping');
    $s->save();
    $s->update_status('active');
    $s->update_status($status);
}
echo "A24_SEED_OK\n";
