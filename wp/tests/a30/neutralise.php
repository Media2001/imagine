<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';
$db = getenv('A30_DB');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1, 'table_decisions' => []];
$count = static fn(): int => (int) $pdo->query(
    "SELECT COUNT(*) FROM wp_users WHERE user_email LIKE 'a13-fictif-%@example.org'"
)->fetchColumn();
$before = $count();
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$engine->anonymiser(bin2hex(random_bytes(24)));
$marker = (int) $pdo->query(
    "SELECT COUNT(*) FROM wp_options WHERE option_name='imagine_staging_disabled_plugins'"
)->fetchColumn();
echo json_encode(['engine_executed' => true, 'marker_count' => $marker,
    'matching_emails_before' => $before, 'matching_emails_after' => $count()], JSON_THROW_ON_ERROR) . "\n";
