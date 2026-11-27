<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';

$db = getenv('A25_DB');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1,
    'table_decisions' => ['wp_a25_unknown_entries' => ['action' => 'garder'],
        'wp_a25_submission_entries' => ['action' => 'garder'],
        'wp_a25_submission_details' => ['action' => 'garder']]];
$counts = static function (PDO $pdo): array {
    return $pdo->query("SELECT COUNT(*) AS n,SUM(comment_author_email <> '') AS emails,
        SUM(comment_author_IP <> '') AS ips FROM wp_comments WHERE comment_type <> 'order_note'")
        ->fetch(PDO::FETCH_ASSOC);
};
$query = static fn(string $sql): array => $pdo->query($sql)->fetchAll(PDO::FETCH_ASSOC);
$knownSql = 'SELECT response FROM wp_fluentform_submissions ORDER BY id';
$unknownSql = 'SELECT message FROM wp_a25_unknown_entries ORDER BY id';
$submissionSql = 'SELECT response FROM wp_a25_submission_entries ORDER BY submission_id';
$detailSql = 'SELECT message FROM wp_a25_submission_details ORDER BY id';
$ordersSql = "SELECT ID FROM wp_posts WHERE post_type='shop_order' ORDER BY ID";
$customersSql = "SELECT post_id,meta_value FROM wp_postmeta WHERE meta_key='_customer_user' ORDER BY meta_id";
$hposSql = "SELECT id,customer_id FROM wp_wc_orders WHERE type='shop_order' ORDER BY id";
$before = $counts($pdo);
$known = $query($knownSql);
$unknown = $query($unknownSql);
$submissions = $query($submissionSql);
$details = $query($detailSql);
$orders = $query($ordersSql);
$customers = $query($customersSql);
$hpos = $query($hposSql);
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$engine->anonymiser(bin2hex(random_bytes(24)));
$after = $counts($pdo);
$guestPreserved = $orders === $query($ordersSql) && $customers === $query($customersSql)
    && $hpos === $query($hposSql);
$markerSql = "SELECT COUNT(*) FROM wp_options WHERE option_name='imagine_staging_disabled_plugins'";
echo json_encode(['neutraliser_and_anonymiser_executed' => true,
    'marker_count' => (int) $pdo->query($markerSql)->fetchColumn(),
    'comments_before' => (int) $before['n'], 'comments_after' => (int) $after['n'],
    'emails_before' => (int) $before['emails'], 'emails_after' => (int) $after['emails'],
    'ip_before' => (int) $before['ips'], 'ip_after' => (int) $after['ips'],
    'known_messages_before' => count($known), 'known_messages_after' => count($query($knownSql)),
    'unknown_messages_before' => count($unknown),
    'unknown_message_preserved' => $unknown === $query($unknownSql),
    'submission_pk_messages_preserved' => count($submissions) === 5 && $submissions === $query($submissionSql),
    'submission_child_rows_preserved' => count($details) === 10 && $details === $query($detailSql),
    'guest_orders_preserved' => $guestPreserved], JSON_THROW_ON_ERROR) . "\n";
