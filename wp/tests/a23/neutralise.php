<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';

$db = getenv('A23_DB');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1];
$before = $pdo->query('SELECT ID,user_login,user_email,user_pass FROM wp_users ORDER BY ID')
    ->fetchAll(PDO::FETCH_ASSOC);
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$engine->anonymiser(bin2hex(random_bytes(24)));
$changed = ['login_changed' => 0, 'email_changed' => 0, 'hash_changed' => 0];
foreach ($before as $row) {
    $statement = $pdo->prepare('SELECT user_login,user_email,user_pass FROM wp_users WHERE ID=?');
    $statement->execute([$row['ID']]);
    $after = $statement->fetch(PDO::FETCH_ASSOC);
    foreach (['login' => 'user_login', 'email' => 'user_email', 'hash' => 'user_pass'] as $key => $column) {
        $changed[$key . '_changed'] += (int) ($row[$column] !== $after[$column]);
    }
}
$marker = (int) $pdo->query(
    "SELECT COUNT(*) FROM wp_options WHERE option_name='imagine_staging_disabled_plugins'"
)->fetchColumn();
echo json_encode(['before_accounts' => count($before), 'changed' => $changed,
    'marker_count' => $marker, 'neutraliser_and_anonymiser_executed' => true], JSON_THROW_ON_ERROR) . "\n";
