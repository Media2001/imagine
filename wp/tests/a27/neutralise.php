<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';

$db = getenv('A27_DB');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1, 'table_decisions' => []];
$count = static fn(string $table): int => (int) $pdo->query('SELECT COUNT(*) FROM ' . $table)->fetchColumn();
$before = $count('wp_woocommerce_payment_tokens');
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$engine->anonymiser(bin2hex(random_bytes(24)));
$marker = "SELECT COUNT(*) FROM wp_options WHERE option_name='imagine_staging_disabled_plugins'";
echo json_encode(
    ['neutraliser_and_anonymiser_executed' => true,
    'tokens_before' => $before, 'tokens_after' => $count('wp_woocommerce_payment_tokens'),
    'tokenmeta_after' => $count('wp_woocommerce_payment_tokenmeta'),
    'marker_count' => (int) $pdo->query($marker)->fetchColumn()],
    JSON_THROW_ON_ERROR
) . "\n";
