<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';
$db = getenv('A21_DB');
if (!preg_match('/\Aa21_(classic|hpos)_test\z/D', (string) $db)) {
    throw new RuntimeException('A21_FIXTURE_DATABASE');
}
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'production_hosts' => ['production.invalid'], 'target_url' => 'https://a02.synthetic.test'];
$store = new Imagine\Staging\PdoStore($pdo, $context);
(new Imagine\Staging\Engine($store, $context, 'wp_'))->neutraliser();
$helper = unserialize((string) $pdo->query("SELECT option_value FROM wp_options WHERE option_name='woocommerce_helper_data'")->fetchColumn(), ['allowed_classes' => false]);
echo json_encode([
    'mark' => $pdo->query("SELECT COUNT(*) FROM wp_options WHERE option_name='imagine_staging_disabled_plugins'")->fetchColumn() == 1,
    'keys' => (int) $pdo->query('SELECT COUNT(*) FROM wp_woocommerce_api_keys')->fetchColumn(),
    'disabled_webhooks' => (int) $pdo->query("SELECT COUNT(*) FROM wp_wc_webhooks WHERE status='disabled'")->fetchColumn(),
    'empty_destinations' => (int) $pdo->query("SELECT COUNT(*) FROM wp_wc_webhooks WHERE delivery_url='' AND secret=''")->fetchColumn(),
    'store_token_empty' => empty($helper['auth']['access_token']),
]) . "\n";
