<?php

declare(strict_types=1);

// Independent read oracle: never bootstraps WordPress or activates any extension.
namespace Imagine\E2E;

$database = getenv('E2E_DATABASE') ?: '';
$storage = getenv('E2E_STORAGE') ?: '';
$mode = getenv('E2E_DB_MODE') ?: 'oracle';
if (!preg_match('/^imagine_e2e_(classic|hpos)_test$/D', $database)
    || !in_array($storage, ['classic', 'hpos'], true)) {
    throw new \RuntimeException('Only the exact freshly generated synthetic databases are allowed');
}
$db = new \PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $database . ';charset=utf8mb4', 'root', '',
    [\PDO::ATTR_ERRMODE => \PDO::ERRMODE_EXCEPTION, \PDO::ATTR_DEFAULT_FETCH_MODE => \PDO::FETCH_ASSOC]);
$rows = static fn (string $sql): array => $db->query($sql)->fetchAll();
$scalar = static fn (string $sql): mixed => $db->query($sql)->fetchColumn();
$meta = static function (string $table, string $idColumn, int $id) use ($db): array {
    $statement = $db->prepare("SELECT meta_key,meta_value FROM $table WHERE $idColumn=?");
    $statement->execute([$id]);
    return $statement->fetchAll(\PDO::FETCH_KEY_PAIR);
};
$put = static function (string $table, array $value) use ($db): void {
    $keys = array_keys($value);
    $sql = 'INSERT INTO `' . $table . '` (`' . implode('`,`', $keys) . '`) VALUES (' . implode(',', array_fill(0, count($keys), '?')) . ')';
    $db->prepare($sql)->execute(array_values($value));
};
$option = static fn (string $name): mixed => $db->query('SELECT option_value FROM wp_options WHERE option_name=' . $db->quote($name))->fetchColumn();
$orderRows = $storage === 'hpos'
    ? $rows("SELECT id,status,currency,total_amount,date_created_gmt,payment_method,customer_id FROM wp_wc_orders WHERE type='shop_order' ORDER BY id")
    : $rows("SELECT ID id,post_status status,post_date_gmt date_created_gmt FROM wp_posts WHERE post_type='shop_order' ORDER BY ID");
$users = $rows('SELECT ID id,user_pass pass_hash,user_login login,user_email email,display_name FROM wp_users ORDER BY ID');

if ($mode === 'mutate') {
    $case = getenv('E2E_RESIDUE_CASE');
    $userId = (int) $users[1]['id'];
    $orderId = (int) $orderRows[0]['id'];
    $orderMeta = $storage === 'hpos' ? 'wp_wc_orders_meta' : 'wp_postmeta';
    $orderKey = $storage === 'hpos' ? 'order_id' : 'post_id';
    switch ($case) {
        case 'service-key':
            $put('wp_options', ['option_name' => 'imagine_e2e_residue', 'option_value' => 'sk_live_SYNTHETIC_E2E_NOT_A_KEY_00000000', 'autoload' => 'no']);
            break;
        case 'user-token':
            $put('wp_usermeta', ['user_id' => $userId, 'meta_key' => '_stripe_customer_id', 'meta_value' => 'cus_SYNTHETICE2ERESIDUE']);
            break;
        case 'order-token':
            $put($orderMeta, [$orderKey => $orderId, 'meta_key' => '_stripe_payment_method', 'meta_value' => 'pm_SYNTHETICE2ERESIDUE']);
            break;
        case 'paypal':
            $put('wp_usermeta', ['user_id' => $userId, 'meta_key' => '_paypal_billing_agreement_id', 'meta_value' => 'B-SYNTHETIC-E2E-NOT-A-TOKEN']);
            break;
        case 'user-email':
            $db->prepare('UPDATE wp_users SET user_email=? WHERE ID=?')->execute(['personnage-fictif@invalid.example', $userId]);
            break;
        case 'order-email':
            if ($storage === 'hpos') {
                $db->prepare('UPDATE wp_wc_orders SET billing_email=? WHERE id=?')->execute(['commande-fictive@invalid.example', $orderId]);
                $db->prepare("UPDATE wp_wc_order_addresses SET email=? WHERE order_id=? AND address_type='billing'")->execute(['commande-fictive@invalid.example', $orderId]);
            } else {
                $db->prepare("UPDATE wp_postmeta SET meta_value=? WHERE post_id=? AND meta_key='_billing_email'")->execute(['commande-fictive@invalid.example', $orderId]);
            }
            break;
        case 'note-email':
            $put('wp_comments', ['comment_post_ID' => $orderId, 'comment_author' => 'Fictif',
                'comment_author_email' => 'note-fictive@invalid.example', 'comment_author_url' => '', 'comment_author_IP' => '192.0.2.123',
                'comment_date' => '2026-11-19 00:00:00', 'comment_date_gmt' => '2026-11-19 00:00:00',
                'comment_content' => 'Note inventée note-fictive@invalid.example', 'comment_approved' => '1',
                'comment_type' => 'order_note', 'comment_agent' => '', 'comment_parent' => 0, 'user_id' => 0]);
            break;
        default:
            throw new \RuntimeException('Unknown explicit residue case');
    }
    echo 'E2E_JSON=' . json_encode(['mutation_applied' => $case], JSON_THROW_ON_ERROR) . "\n";
    return;
}

if ($mode === 'snapshot') {
    $orders = [];
    foreach ($orderRows as $order) {
        $id = (int) $order['id'];
        $data = $storage === 'classic' ? $meta('wp_postmeta', 'post_id', $id) : [];
        $addresses = [];
        if ($storage === 'hpos') {
            foreach ($rows('SELECT address_type,country FROM wp_wc_order_addresses WHERE order_id=' . $id) as $address) {
                $addresses[$address['address_type']] = $address['country'];
            }
        }
        $items = [];
        foreach ($rows("SELECT order_item_id FROM wp_woocommerce_order_items WHERE order_item_type='line_item' AND order_id=$id ORDER BY order_item_id") as $item) {
            $values = $meta('wp_woocommerce_order_itemmeta', 'order_item_id', (int) $item['order_item_id']);
            $items[] = ['product' => (int) ($values['_product_id'] ?? 0), 'quantity' => (string) ($values['_qty'] ?? ''),
                'total' => number_format((float) ($values['_line_total'] ?? 0), 2, '.', ''),
                'tax' => number_format((float) ($values['_line_tax'] ?? 0), 2, '.', '')];
        }
        $orders[] = ['id' => $id, 'status' => $order['status'], 'created_gmt' => $order['date_created_gmt'],
            'total' => number_format((float) ($order['total_amount'] ?? $data['_order_total'] ?? 0), 2, '.', ''),
            'currency' => $order['currency'] ?? $data['_order_currency'] ?? '',
            'payment_method' => $order['payment_method'] ?? $data['_payment_method'] ?? '',
            'billing_country' => $addresses['billing'] ?? $data['_billing_country'] ?? '',
            'shipping_country' => $addresses['shipping'] ?? $data['_shipping_country'] ?? '', 'items' => $items];
    }
    foreach ($users as &$user) {
        $values = $meta('wp_usermeta', 'user_id', (int) $user['id']);
        foreach (['first_name', 'last_name', 'billing_country', 'shipping_country'] as $key) {
            $user[$key] = $values[$key] ?? '';
        }
    }
    unset($user);
    echo 'E2E_JSON=' . json_encode(['orders' => $orders, 'users' => $users], JSON_THROW_ON_ERROR) . "\n";
    return;
}

$hits = [];
foreach ($db->query('SHOW TABLES')->fetchAll(\PDO::FETCH_COLUMN) as $table) {
    $quoted = '`' . str_replace('`', '``', $table) . '`';
    foreach ($rows('SHOW COLUMNS FROM ' . $quoted) as $column) {
        if (!preg_match('/char|text|blob|json|enum|set/i', $column['Type'])) {
            continue;
        }
        $columnQuoted = '`' . str_replace('`', '``', $column['Field']) . '`';
        foreach ($db->query('SELECT ' . $columnQuoted . ' FROM ' . $quoted)->fetchAll(\PDO::FETCH_COLUMN) as $value) {
            if (!is_string($value)) { continue; }
            foreach (['service-key' => '/(?:sk_live_|pk_live_|rk_live_|whsec_|xkeysib-)[A-Za-z0-9_-]+/',
                'payment-identifier' => '/(?:cus_|pm_|src_|seti_)[A-Za-z0-9]+/',
                'paypal-identifier' => '/[BI]-SYNTHETIC-E2E-NOT-A-TOKEN/',
                'invented-offdomain-email' => '/[A-Z0-9._%+-]+@invalid\.example\b/i',
                'invented-documentation-ip' => '/192\.0\.2\.123/'] as $kind => $pattern) {
                if ($kind === 'invented-documentation-ip' && getenv('E2E_ORACLE_PHASE') !== 'after') { continue; }
                if (preg_match($pattern, $value)) {
                    $key = $table . '.' . $column['Field'] . ':' . $kind;
                    $hits[$key] = ($hits[$key] ?? 0) + 1;
                }
            }
        }
    }
}
$badUsers = count(array_filter($users, static fn (array $u): bool => !preg_match('/^[^@]+@example\.org$/D', $u['email'])));
$badOrders = 0;
foreach ($orderRows as $order) {
    $email = $storage === 'hpos'
        ? $scalar('SELECT billing_email FROM wp_wc_orders WHERE id=' . (int) $order['id'])
        : ($meta('wp_postmeta', 'post_id', (int) $order['id'])['_billing_email'] ?? '');
    if (!preg_match('/^[^@]+@example\.org$/D', (string) $email)) { ++$badOrders; }
}
$cron = unserialize((string) $option('cron'), ['allowed_classes' => false]);
$cronOutbound = 0;
foreach (is_array($cron) ? $cron : [] as $hooks) {
    if (is_array($hooks) && isset($hooks['imagine_e2e_outbound_cron'])) { ++$cronOutbound; }
}
$result = ['residue_hits' => $hits, 'bad_user_emails' => $badUsers, 'bad_order_emails' => $badOrders,
    'pending_outbound' => (int) $scalar("SELECT COUNT(*) FROM wp_actionscheduler_actions WHERE status='pending' AND hook='imagine_e2e_outbound'"),
    'cron_outbound' => $cronOutbound, 'active_webhooks' => (int) $scalar("SELECT COUNT(*) FROM wp_wc_webhooks WHERE status='active'"),
    'payment_tokens' => (int) $scalar('SELECT COUNT(*) FROM wp_woocommerce_payment_tokens'),
    'user_count' => count($users), 'order_count' => count($orderRows),
    'sessions' => (int) $scalar("SELECT COUNT(*) FROM wp_usermeta WHERE meta_key='session_tokens'"),
    'blog_public' => $option('blog_public'), 'home' => $option('home'), 'siteurl' => $option('siteurl')];
echo 'E2E_JSON=' . json_encode($result, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES) . "\n";
