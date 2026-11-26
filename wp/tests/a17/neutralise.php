<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';

$db = getenv('A17_DB');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1];
$before = (int) $pdo->query("SELECT COUNT(*) FROM wp_usermeta WHERE meta_key='_application_passwords'")->fetchColumn();
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$after = (int) $pdo->query("SELECT COUNT(*) FROM wp_usermeta WHERE meta_key='_application_passwords'")->fetchColumn();
$marker = (int) $pdo->query(
    "SELECT COUNT(*) FROM wp_options WHERE option_name='imagine_staging_disabled_plugins'"
)->fetchColumn();
$engine->anonymiser(bin2hex(random_bytes(24)));
echo json_encode(['application_password_rows_before' => $before, 'application_password_rows_after' => $after,
    'neutralisation_marker_count' => $marker, 'neutraliser_and_anonymiser_executed' => true], JSON_THROW_ON_ERROR);
