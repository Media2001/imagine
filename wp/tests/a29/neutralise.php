<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';

$db = getenv('A29_DB');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1, 'table_decisions' => []];
$count = static function (string $status) use ($pdo): int {
    $q = $pdo->prepare('SELECT COUNT(*) FROM wp_actionscheduler_actions WHERE status=?');
    $q->execute([$status]);
    return (int) $q->fetchColumn();
};
$cronCount = static function () use ($pdo): int {
    $raw = $pdo->query("SELECT option_value FROM wp_options WHERE option_name='cron'")->fetchColumn();
    $cron = unserialize($raw, ['allowed_classes' => false]);
    unset($cron['version']);
    $n = 0;
    foreach ($cron as $hooks) {
        foreach ($hooks as $events) {
            $n += count($events);
        }
    }
    return $n;
};
$before = ['cron' => $cronCount(), 'pending' => $count('pending'), 'failed' => $count('failed')];
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$engine->anonymiser(bin2hex(random_bytes(24)));
$after = ['cron' => $cronCount(), 'pending' => $count('pending'), 'failed' => $count('failed'),
    'canceled' => $count('canceled')];
$marker = (int) $pdo->query("SELECT COUNT(*) FROM wp_options WHERE option_name='imagine_staging_disabled_plugins'")->fetchColumn();
echo json_encode(['neutraliser_and_anonymiser_executed' => true, 'before' => $before,
    'after' => $after, 'marker_count' => $marker], JSON_THROW_ON_ERROR) . "\n";
