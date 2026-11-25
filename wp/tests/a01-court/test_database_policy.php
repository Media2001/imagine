<?php

declare(strict_types=1);

require '/subject/lib.php';
require '/opt/fixtures.php';

$store = fixture();
$store->tables['x_options'] = array_values(array_filter($store->tables['x_options'], static fn (array $row): bool => !in_array($row['option_name'], ['active_plugins', 'cron'], true)));
$disabled = ['worker/init.php', 'wordfence/wordfence.php', 'fluent-smtp/fluent-smtp.php', 'matomo/matomo.php', 'woocommerce-gateway-stripe/woocommerce-gateway-stripe.php'];
$kept = ['wp-all-export/wp-all-export.php', 'wp-all-import-pro/wp-all-import-pro.php', 'woo-order-export-lite/woocommerce-order-export.php'];
$store->tables['x_options'][] = ['option_id' => 800, 'option_name' => 'active_plugins', 'option_value' => serialize(array_merge($disabled, $kept))];
$store->tables['x_options'][] = ['option_id' => 801, 'option_name' => 'cron', 'option_value' => serialize([123 => ['pmxe_cron' => ['FICTION']]])];
foreach (['admin_email', 'new_admin_email', 'woocommerce_email_from_address', 'woocommerce_stock_email_recipient'] as $i => $name) {
    $store->tables['x_options'][] = ['option_id' => 810 + $i, 'option_name' => $name, 'option_value' => 'FICTION_ADMIN_SENTINEL@example.org'];
}
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true, 'database' => 'invented_staging', 'target_url' => 'https://invented.test', 'production_hosts' => ['source.invalid']];
foreach (['pmxe_cron', 'pmxi_cron', 'woe_cron_export'] as $i => $hook) {
    $action = $store->tables['x_actionscheduler_actions'][0];
    $action['action_id'] = 800 + $i;
    $action['hook'] = $hook;
    $action['status'] = 'pending';
    $store->tables['x_actionscheduler_actions'][] = $action;
}
$engine = new Imagine\Staging\Engine($store, $context, 'x_');
$engine->neutraliser();
$engine->anonymiser('FICTION-test-password-only-2026');
$options = array_column($store->rows('x_options'), 'option_value', 'option_name');
if (unserialize($options['active_plugins']) !== $kept) {
    throw new RuntimeException('REMOTE_SECURITY_PLUGINS_NOT_DISABLED');
}
if (unserialize($options['cron']) !== []) {
    throw new RuntimeException('EXPORT_CRON_NOT_REMOVED');
}
foreach (['admin_email', 'new_admin_email', 'woocommerce_email_from_address', 'woocommerce_stock_email_recipient'] as $name) {
    if ($options[$name] !== 'imagine-test-admin@example.org') {
        throw new RuntimeException('OPERATIONAL_OPTION_EMAIL_NOT_ANONYMISED');
    }
}
$stripe = unserialize($options['woocommerce_stripe_settings']);
if ($stripe['secret_key'] !== '' || $stripe['testmode'] !== 'yes') {
    throw new RuntimeException('STRIPE_NOT_NEUTRALISED');
}
foreach ($store->rows('x_actionscheduler_actions') as $row) {
    if (preg_match('/^(?:pmxe_|pmxi_|woe_)/', $row['hook'] ?? '')) {
        throw new RuntimeException('EXPORT_IMPORT_SCHEDULE_NOT_DELETED');
    }
    if ($row['args'] !== '[]' || ($row['extended_args'] ?? null) !== null || in_array($row['status'], ['pending', 'in-progress'], true)) {
        throw new RuntimeException('AS_ARGUMENTS_NOT_REMOVED');
    }
}
if ($store->rows('x_actionscheduler_logs') !== []) {
    throw new RuntimeException('AS_LOGS_NOT_REMOVED');
}
foreach ($store->rows('x_comments') as $row) {
    if ($row['comment_author_IP'] !== '' || !str_ends_with($row['comment_author_email'], '@example.org')) {
        throw new RuntimeException('COMMENT_NOT_ANONYMISED');
    }
}
$store->columns['x_fiction_unknown'] = ['id', 'email'];
$store->tables['x_fiction_unknown'] = [['id' => 1, 'email' => 'FICTION_NEW_TABLE@example.org']];
$context['table_policy_version'] = 1;
$closed = new Imagine\Staging\Engine($store, $context, 'x_');
$closed->neutraliser();
if ($store->rows('x_fiction_unknown') !== []) {
    throw new RuntimeException('NATIVE_UNKNOWN_DEFAULT_NOT_CLOSED');
}
$store->tables['x_fiction_unknown'][] = ['id' => 2, 'email' => 'FICTION_RECREATED@example.org'];
if (!in_array('TABLE_STRUCTURE_NON_VIDE', $closed->verifier(null)['issues'], true)) {
    throw new RuntimeException('RECREATED_UNKNOWN_TABLE_NOT_REFUSED');
}
echo "A01_3_NATIVE_POLICY_PASS\n";
