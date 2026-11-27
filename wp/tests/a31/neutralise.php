<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';
$db = getenv('A31_DB');
$storage = getenv('A31_STORAGE');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1, 'table_decisions' => []];
$table = $storage === 'hpos' ? 'wp_wc_orders_meta' : 'wp_postmeta';
$count = static fn (string $key): int => (int) $pdo->query(
    "SELECT COUNT(*) FROM {$table} WHERE meta_key='" . $key . "'"
)->fetchColumn();
$structure = static function () use ($pdo, $storage): string {
    $query = $storage === 'hpos'
        ? "SELECT id,type,status,date_created_gmt,customer_id,parent_order_id FROM wp_wc_orders ORDER BY id"
        : "SELECT ID,post_type,post_status,post_date_gmt,post_parent FROM wp_posts"
            . " WHERE post_type IN ('shop_order','shop_order_refund','shop_subscription') ORDER BY ID";
    $rows = $pdo->query($query)->fetchAll(PDO::FETCH_ASSOC);
    return hash('sha256', json_encode($rows, JSON_THROW_ON_ERROR));
};
$countNumericRenewal = static fn (): int => (int) $pdo->query(
    "SELECT COUNT(*) FROM {$table} WHERE meta_key='_subscription_renewal'"
    . " AND meta_value REGEXP '^[1-9][0-9]*$'"
)->fetchColumn();
$before = $structure();
$extension = $count('_subscription_stripe_subscription_id');
$renewal = $countNumericRenewal();
$renewalRows = $count('_subscription_renewal');
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$engine->anonymiser(bin2hex(random_bytes(24)));
$marker = (int) $pdo->query(
    "SELECT COUNT(*) FROM wp_options WHERE option_name='imagine_staging_disabled_plugins'"
)->fetchColumn();
echo json_encode(['neutraliser_and_anonymiser_executed' => true,
    'structure_before_sha256' => $before, 'structure_after_sha256' => $structure(),
    'extension_relation_before' => $extension,
    'extension_relation_after' => $count('_subscription_stripe_subscription_id'),
    'renewal_relation_before' => $renewal, 'renewal_relation_after' => $countNumericRenewal(),
    'renewal_rows_before' => $renewalRows, 'renewal_rows_after' => $count('_subscription_renewal'),
    'opaque_renewal_before' => $renewalRows - $renewal,
    'opaque_renewal_after' => $count('_subscription_renewal') - $countNumericRenewal(),
    'marker_count' => $marker], JSON_THROW_ON_ERROR) . "\n";
