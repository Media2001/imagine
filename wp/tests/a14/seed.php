<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
$ids = [];
foreach (['alice', 'bob', 'carol', 'technical', 'local', 'firstlast', 'unmatched', 'shareda', 'sharedb', 'invalid'] as $name) {
    $ids[$name] = wp_insert_user(['user_login' => 'a14-fictif-' . $name, 'user_email' => $name . '@example.org', 'user_pass' => wp_generate_password(40)]);
    if (is_wp_error($ids[$name])) {
        throw new RuntimeException('A14_SEED_USER');
    }
}
update_user_meta($ids['technical'], 'imagine_sans_email', '1');
global $wpdb;
$wpdb->update($wpdb->users, ['user_email' => ' shared@example.org '], ['ID' => $ids['shareda']]);
$wpdb->update($wpdb->users, ['user_email' => 'SHARED@example.org'], ['ID' => $ids['sharedb']]);
$wpdb->update($wpdb->users, ['user_email' => 'invalid'], ['ID' => $ids['invalid']]);
foreach (['alice' => 'active', 'bob' => 'cancelled', 'carol' => 'on-hold'] as $name => $state) {
    $s = wcs_create_subscription(['customer_id' => $ids[$name], 'status' => 'pending', 'billing_period' => 'month', 'billing_interval' => 1]);
    if (is_wp_error($s)) {
        throw new RuntimeException('A14_SEED_SUBSCRIPTION');
    }
    $s->set_requires_manual_renewal(true);
    $s->save();
    $s->update_status('active');
    if ($state !== 'active') {
        $s->update_status($state);
    }
}
$active = [];
foreach (['alice', 'bob', 'carol'] as $name) {
    $active[$name] = wcs_user_has_subscription($ids[$name], '', 'active');
}
echo 'A14_JSON=' . json_encode(['active' => $active, 'accounts' => count_users()['total_users'], 'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled()]) . "\n";
