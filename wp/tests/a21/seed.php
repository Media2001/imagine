<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->prefix}woocommerce_api_keys");
$wpdb->query("DELETE FROM {$wpdb->prefix}wc_webhooks");
foreach ([['read', null], ['read_write', '2024-01-01 00:00:00']] as [$permission, $access]) {
    $ok = $wpdb->insert($wpdb->prefix . 'woocommerce_api_keys', [
        'user_id' => 1, 'description' => 'A21_DESCRIPTION_PRIVATE_CANARY', 'permissions' => $permission,
        'consumer_key' => hash('sha256', 'A21_KEY_PRIVATE_CANARY' . $permission),
        'consumer_secret' => 'A21_SECRET_PRIVATE_CANARY', 'truncated_key' => 'CANARY',
        'nonces' => 'A21_NONCE_PRIVATE_CANARY', 'last_access' => $access,
    ]);
    if ($ok !== 1) {
        throw new RuntimeException('A21_FIXTURE_KEYS');
    }
}
foreach (
    [
    ['active', 'order.created', 'https://external.example.org/A21_DELIVERY_PRIVATE_CANARY'],
    ['paused', 'product.updated', 'https://paused.example.org/A21_PAUSED_PRIVATE_CANARY'],
    ['active', 'order.updated', home_url('/A21_SELF_PRIVATE_CANARY')],
    ['disabled', 'customer.created', 'https://disabled.example.org/A21_DISABLED_PRIVATE_CANARY'],
    ] as [$status, $topic, $url]
) {
    $hook = new WC_Webhook();
    $hook->set_name('A21_WEBHOOK_DESCRIPTION_PRIVATE_CANARY');
    $hook->set_user_id(1);
    $hook->set_status($status);
    $hook->set_topic($topic);
    $hook->set_delivery_url($url);
    $hook->set_secret('A21_WEBHOOK_SECRET_PRIVATE_CANARY');
    $hook->set_pending_delivery(false);
    $hook->save();
    $read = new WC_Webhook($hook->get_id());
    if (
        $read->get_status('edit') !== $status || $read->get_topic('edit') !== $topic
        || $read->get_delivery_url('edit') !== $url
    ) {
        throw new RuntimeException('A21_FIXTURE_WEBHOOK');
    }
}
// Action-topic names are operator-controlled too: deliberately corrupt only this synthetic row.
$wpdb->query("UPDATE {$wpdb->prefix}wc_webhooks SET topic='action.A21_TOPIC_PRIVATE_CANARY' WHERE status='disabled'");
WC_Helper_Options::update('auth', ['access_token' => 'A21_STORE_TOKEN_PRIVATE_CANARY',
    'access_token_secret' => 'A21_STORE_SECRET_PRIVATE_CANARY', 'site_id' => 987654]);
update_option('timezone_string', 'Europe/Paris');
$oracle = ['keys' => (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}woocommerce_api_keys"),
    'webhooks' => (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wc_webhooks"),
    'store_connected_native' => WC_Helper::is_site_connected()];
echo 'A21_JSON=' . json_encode($oracle) . "\n";
