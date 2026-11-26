<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
$user = wp_insert_user(['user_login' => 'a18-fictif', 'user_email' => 'a18@example.org',
    'user_pass' => wp_generate_password(40), 'display_name' => 'A18_PERSONAL_CANARY']);
if (is_wp_error($user)) {
    throw new RuntimeException('A18_FIXTURE_USER');
}
update_user_meta($user, '_a18_card', '4242 4242 4242 4242');
update_user_meta($user, '_a18_rr', '85.07.30-033.28');
update_user_meta($user, '_a18_canary', 'A18_PRIVATE_CANARY');
$order = wc_create_order(['customer_id' => $user]);
$order->add_meta_data('_a18_bank', 'BE68539007547034');
$order->add_meta_data('_a18_bank', 'BE69539007547034');
$order->add_meta_data('_a18_shared_bank', 'BE68539007547034');
$order->save();
// Residual physical rows in the inactive store: deliberately bypass the active CRUD API.
global $wpdb;
$activeHpos = get_option('woocommerce_custom_orders_table_enabled') === 'yes';
foreach ([901801 => 'shop_order', 901802 => 'shop_subscription'] as $id => $type) {
    if ($activeHpos) {
        $wpdb->insert($wpdb->posts, ['ID' => $id, 'post_type' => $type, 'post_status' => 'wc-pending',
            'post_content' => '', 'post_excerpt' => '', 'to_ping' => '', 'pinged' => '',
            'post_content_filtered' => '']);
        $table = $wpdb->postmeta;
        $owner = 'post_id';
    } else {
        $wpdb->insert($wpdb->prefix . 'wc_orders', ['id' => $id, 'type' => $type,
            'status' => 'wc-pending', 'currency' => 'EUR', 'customer_id' => 0]);
        $table = $wpdb->prefix . 'wc_orders_meta';
        $owner = 'order_id';
    }
    $wpdb->insert($table, [$owner => $id, 'meta_key' => '_a18_inactive_bank', 'meta_value' => 'BE68539007547034']);
    $wpdb->insert($table, [$owner => $id, 'meta_key' => '_a18_inactive_bank', 'meta_value' => 'BE69539007547034']);
    if ($type === 'shop_order') {
        $wpdb->insert($table, [$owner => $id, 'meta_key' => '_a18_shared_bank', 'meta_value' => 'BE68539007547034']);
    }
    if ($wpdb->last_error !== '') {
        throw new RuntimeException('A18_FIXTURE_INACTIVE_STORE');
    }
}
$sub = wcs_create_subscription(['customer_id' => $user, 'status' => 'pending',
    'billing_period' => 'month', 'billing_interval' => 1]);
$sub->update_meta_data('_a18_bank', 'BE68 5390 0754 7034');
$sub->save();
update_option('a18_bank_setting', ['value' => 'BE68539007547034', 'canary' => 'A18_PRIVATE_CANARY']);
update_option('a18_invalid_setting', 'BE69539007547034');
$token = new WC_Payment_Token_CC();
$token->set_user_id($user);
$token->set_gateway_id('a18_fixture');
$token->set_token('A18_PRIVATE_TOKEN_CANARY');
$token->set_card_type('visa');
$token->set_last4('4242');
$token->set_expiry_month('12');
$token->set_expiry_year('2030');
$token->save();
$uploads = wp_upload_dir(null, true, true)['basedir'];
foreach (['exports', 'A18_EMPTY_CANARY', 'A18_PERSONAL_FOLDER_CANARY', '2026'] as $dir) {
    wp_mkdir_p($uploads . '/' . $dir);
}
foreach (['a.csv' => 'ABC', 'b.csv' => 'DEFG', 'c.log' => 'HIJKL'] as $name => $text) {
    file_put_contents($uploads . '/exports/A18_FILE_CANARY-' . $name, $text);
}
file_put_contents($uploads . '/A18_PERSONAL_FOLDER_CANARY/A18_FILE_CANARY.txt', 'XXXX');
file_put_contents($uploads . '/2026/A18_YEAR_CANARY.csv', 'EXCLUDED');
echo 'A18_JSON=' . json_encode(['uploads' => $uploads]) . "\n";
