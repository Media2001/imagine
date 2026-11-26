<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';
$db = getenv('A24_DB');
$hpos = getenv('A24_STORAGE') === 'hpos';
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1];
$fields = ['first_name', 'last_name', 'company', 'country', 'address_1', 'address_2',
    'city', 'state', 'postcode', 'phone'];
$read = static function () use ($pdo, $hpos, $fields): array {
    $result = [];
    foreach (['shipping', 'billing'] as $kind) {
        foreach ($fields as $field) {
            $values = $hpos
                ? $pdo->query("SELECT order_id,`{$field}` AS value FROM wp_wc_order_addresses"
                    . " WHERE address_type='{$kind}' ORDER BY order_id")->fetchAll(PDO::FETCH_KEY_PAIR)
                : $pdo->query("SELECT post_id,meta_value FROM wp_postmeta"
                    . " WHERE meta_key='_{$kind}_{$field}' ORDER BY post_id")->fetchAll(PDO::FETCH_KEY_PAIR);
            $result[$kind . '_' . $field] = $values;
        }
    }
    foreach ($fields as $field) {
        $result['customer_' . $field] = $pdo->query("SELECT user_id,meta_value FROM wp_usermeta"
            . " WHERE meta_key='shipping_{$field}' ORDER BY user_id")->fetchAll(PDO::FETCH_KEY_PAIR);
    }
    return $result;
};
$before = $read();
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$engine->anonymiser(bin2hex(random_bytes(24)));
$after = $read();
$changed = [];
$nonempty = [];
foreach ($before as $key => $rows) {
    $changed[$key] = 0;
    $nonempty[$key] = 0;
    foreach ($rows as $id => $value) {
        $changed[$key] += (int) ($value !== ($after[$key][$id] ?? null));
    }
    foreach ($after[$key] as $value) {
        $nonempty[$key] += (int) ($value !== '' && $value !== null);
    }
}
$marker = (int) $pdo->query("SELECT COUNT(*) FROM wp_options"
    . " WHERE option_name='imagine_staging_disabled_plugins'")->fetchColumn();
echo json_encode(
    ['neutraliser_and_anonymiser_executed' => true, 'marker_count' => $marker,
    'changed_counts' => $changed, 'remaining_nonempty_counts' => $nonempty,
    'shipping_countries_preserved' => $before['shipping_country'] === $after['shipping_country'],
    'billing_countries_preserved' => $before['billing_country'] === $after['billing_country'],
    'customer_countries_preserved' => $before['customer_country'] === $after['customer_country']],
    JSON_THROW_ON_ERROR
) . "\n";
