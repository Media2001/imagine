<?php

declare(strict_types=1);

require '/subject/lib.php';
require '/opt/fixtures.php';

$store = fixture();
$store->tables['x_options'] = array_values(array_filter($store->tables['x_options'], static fn (array $row): bool => !in_array($row['option_name'], ['active_plugins', 'cron'], true)));
$disabled = ['worker/init.php', 'wordfence/wordfence.php', 'fluent-smtp/fluent-smtp.php', 'matomo/matomo.php'];
$kept = ['wp-all-export/wp-all-export.php', 'wp-all-import-pro/wp-all-import-pro.php', 'woo-order-export-lite/woocommerce-order-export.php', 'woocommerce-gateway-stripe/woocommerce-gateway-stripe.php'];
$store->tables['x_options'][] = ['option_id' => 800, 'option_name' => 'active_plugins', 'option_value' => serialize(array_merge($disabled, $kept))];
$store->tables['x_options'][] = ['option_id' => 801, 'option_name' => 'cron', 'option_value' => serialize([123 => ['pmxe_cron' => ['FICTION']]])];
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true, 'database' => 'invented_staging', 'target_url' => 'https://invented.test', 'production_hosts' => ['source.invalid']];
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
$stripe = unserialize($options['woocommerce_stripe_settings']);
if ($stripe['secret_key'] !== '' || $stripe['testmode'] !== 'yes') {
    throw new RuntimeException('STRIPE_NOT_NEUTRALISED');
}
foreach ($store->rows('x_actionscheduler_actions') as $row) {
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
echo "A01_3_NATIVE_POLICY_PASS\n";
