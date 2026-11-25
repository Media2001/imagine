<?php

declare(strict_types=1);

namespace Imagine\CouponInventory;

use Imagine\Audit\Audit;

final class Inventory
{
    private \PDO $db;
    private string $prefix;
    private array $tables;

    public function __construct(string $site)
    {
        $file = $site . '/wp-config.php';
        if (is_link($file) || realpath($file) !== $file || !is_file($file) || filesize($file) > 1048576) {
            throw new \RuntimeException('A10_CONFIG_UNSAFE');
        }
        $config = Audit::config(file_get_contents($file));
        $this->prefix = $config['table_prefix'];
        $host = $config['DB_HOST'];
        if (preg_match('~\Alocalhost:(/[^;\x00-\x1f]+)\z~D', $host, $match)) {
            $dsn = 'mysql:unix_socket=' . $match[1];
        } elseif (preg_match('/\A([A-Za-z0-9_.-]+)(?::([0-9]{1,5}))?\z/D', $host, $match)) {
            $dsn = 'mysql:host=' . $match[1] . ';port=' . ($match[2] ?? '3306');
        } else {
            throw new \RuntimeException('A10_DB_HOST_UNSUPPORTED');
        }
        if (!preg_match('/\A[A-Za-z0-9_-]+\z/D', $config['DB_NAME'])) {
            throw new \RuntimeException('A10_DB_NAME_UNSUPPORTED');
        }
        $this->db = new \PDO($dsn . ';dbname=' . $config['DB_NAME'] . ';charset=utf8mb4', $config['DB_USER'], $config['DB_PASSWORD'], [
            \PDO::ATTR_ERRMODE => \PDO::ERRMODE_EXCEPTION,
            \PDO::ATTR_EMULATE_PREPARES => false,
            \PDO::MYSQL_ATTR_MULTI_STATEMENTS => false,
            \PDO::ATTR_TIMEOUT => 10,
        ]);
        unset($config);
        $this->db->exec('SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ');
        $this->db->exec('SET SESSION TRANSACTION READ ONLY');
        $this->db->beginTransaction();
        $this->tables = [];
        foreach ($this->select('SELECT TABLE_NAME,ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE=\'BASE TABLE\'') as $row) {
            if ($row['ENGINE'] !== 'InnoDB') {
                throw new \RuntimeException('A10_TRANSACTIONAL_TABLES_REQUIRED');
            }
            $this->tables[] = $row['TABLE_NAME'];
        }
        if (in_array($this->prefix . 'blogs', $this->tables, true) || $this->option('ms_files_rewriting') !== '') {
            throw new \RuntimeException('A10_MULTISITE_UNSUPPORTED');
        }
    }

    public function __destruct()
    {
        if (isset($this->db) && $this->db->inTransaction()) {
            $this->db->rollBack();
        }
    }

    private function select(string $sql, array $params = []): array
    {
        if (!str_starts_with($sql, 'SELECT ')) {
            throw new \RuntimeException('A10_NON_SELECT_FORBIDDEN');
        }
        $statement = $this->db->prepare($sql);
        $statement->execute($params);
        return $statement->fetchAll(\PDO::FETCH_ASSOC);
    }

    private function table(string $suffix): string
    {
        $name = $this->prefix . $suffix;
        if (!in_array($name, $this->tables, true)) {
            throw new \RuntimeException('A10_TABLE_MISSING');
        }
        return '`' . $name . '`';
    }

    private function option(string $name): string
    {
        $rows = $this->select('SELECT option_value FROM ' . $this->table('options') . ' WHERE option_name=?', [$name]);
        return $rows[0]['option_value'] ?? '';
    }

    private function metadata(int $id): array
    {
        // Never read _used_by, descriptions, authors, customers or arbitrary plugin metadata.
        $keys = ['discount_type', 'coupon_amount', 'usage_count', 'usage_limit', 'usage_limit_per_user',
            'limit_usage_to_x_items', 'product_ids', 'exclude_product_ids', 'product_categories',
            'exclude_product_categories', 'customer_email', 'date_expires', 'expiry_date',
            'individual_use', 'free_shipping', 'exclude_sale_items', 'minimum_amount', 'maximum_amount',
            '_wcs_number_payments'];
        $rows = $this->select('SELECT meta_key,meta_value FROM ' . $this->table('postmeta') . ' WHERE post_id=? AND meta_key IN (' . implode(',', array_fill(0, count($keys), '?')) . ')', [$id, ...$keys]);
        $meta = array_fill_keys($keys, '');
        $seen = [];
        foreach ($rows as $row) {
            if (isset($seen[$row['meta_key']])) {
                throw new \RuntimeException('A10_DUPLICATE_COUPON_META');
            }
            $seen[$row['meta_key']] = true;
            $meta[$row['meta_key']] = $row['meta_value'] ?? '';
        }
        return $meta;
    }

    private function zone(): \DateTimeZone
    {
        $name = $this->option('timezone_string');
        if ($name !== '') {
            return new \DateTimeZone($name);
        }
        $offset = $this->option('gmt_offset');
        if ($offset === '' || $offset === '0') {
            return new \DateTimeZone('UTC');
        }
        if (!preg_match('/\A-?[0-9]{1,2}(?:\.(?:25|5|75))?\z/D', $offset) || abs((float) $offset) > 14) {
            throw new \RuntimeException('A10_TIMEZONE_INVALID');
        }
        $seconds = (int) round((float) $offset * 3600);
        return new \DateTimeZone(sprintf('%s%02d:%02d', $seconds < 0 ? '-' : '+', intdiv(abs($seconds), 3600), intdiv(abs($seconds) % 3600, 60)));
    }

    private static function date(string $value): ?string
    {
        if ($value === '0000-00-00 00:00:00') {
            return null;
        }
        if (!preg_match('/\A[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\z/D', $value)) {
            throw new \RuntimeException('A10_DATE_INVALID');
        }
        return str_replace(' ', 'T', $value) . 'Z';
    }

    public function collect(): array
    {
        $hpos = $this->option('woocommerce_custom_orders_table_enabled') === 'yes';
        $orders = $this->table($hpos ? 'wc_orders' : 'posts');
        $id = $hpos ? 'id' : 'ID';
        $type = $hpos ? 'type' : 'post_type';
        $status = $hpos ? 'status' : 'post_status';
        $date = $hpos ? 'date_created_gmt' : 'post_date_gmt';
        $items = $this->table('woocommerce_order_items');
        $posts = $this->table('posts');
        $now = new \DateTimeImmutable($this->select('SELECT UTC_TIMESTAMP() AS now')[0]['now'], new \DateTimeZone('UTC'));
        $cutoff = Projection::cutoff($now);
        $zone = $this->zone();
        $codes = [];
        $expired = [];
        $never = [];
        foreach ($this->select("SELECT ID,post_title,post_status,post_date_gmt,post_modified_gmt FROM $posts WHERE post_type='shop_coupon' ORDER BY BINARY post_title,ID") as $coupon) {
            $meta = $this->metadata((int) $coupon['ID']);
            $code = $coupon['post_title'];
            $typeValue = $meta['discount_type'];
            // Names are the sole expressly permitted setting labels; not descriptions.
            $subscriptions = ['active' => 0, 'on_hold' => 0, 'pending' => 0, 'pending_cancel' => 0];
            $map = ['wc-active' => 'active', 'wc-on-hold' => 'on_hold', 'wc-pending' => 'pending', 'wc-pending-cancel' => 'pending_cancel'];
            $join = " FROM $orders o JOIN $items i ON i.order_id=o.$id WHERE i.order_item_type='coupon' AND BINARY LOWER(i.order_item_name)=BINARY LOWER(?)";
            foreach ($this->select("SELECT o.$status AS status,COUNT(DISTINCT o.$id) AS n" . $join . " AND o.$type='shop_subscription' AND o.$status IN ('wc-active','wc-on-hold','wc-pending','wc-pending-cancel') GROUP BY o.$status", [$code]) as $row) {
                $subscriptions[$map[$row['status']]] = (int) $row['n'];
            }
            $orderCount = $this->select("SELECT COUNT(DISTINCT o.$id) AS n" . $join . " AND o.$type='shop_order' AND o.$status NOT IN ('trash','auto-draft') AND o.$date>=? AND o.$date<=?", [$code, $cutoff, $now->format('Y-m-d H:i:s')])[0]['n'];
            $expiry = Projection::expiry($meta['date_expires'] !== '' ? $meta['date_expires'] : $meta['expiry_date'], $zone);
            $count = Projection::number($meta['usage_count'] === '' ? '0' : $meta['usage_count']);
            $row = ['code' => $code, 'status' => Audit::identifier($coupon['post_status']),
                'type' => Audit::identifier($typeValue), 'amount' => Projection::decimal($meta['coupon_amount']),
                'amount_unit' => in_array($typeValue, ['percent', 'recurring_percent', 'sign_up_fee_percent'], true) ? 'percent' : (Projection::recurring($typeValue) === null ? 'unknown' : 'store_currency'),
                'date_created_utc' => self::date($coupon['post_date_gmt']), 'date_modified_utc' => self::date($coupon['post_modified_gmt']),
                'date_expires_utc' => $expiry, 'usage_count' => $count,
                'usage_limit' => Projection::number($meta['usage_limit'] === '' ? '0' : $meta['usage_limit']),
                'usage_limit_per_user' => Projection::number($meta['usage_limit_per_user'] === '' ? '0' : $meta['usage_limit_per_user']),
                'item_limit' => ($limit = Projection::number($meta['limit_usage_to_x_items'])) ? $limit : null,
                'product_ids' => Projection::ids($meta['product_ids']), 'excluded_product_ids' => Projection::ids($meta['exclude_product_ids']),
                'product_categories' => Projection::ids($meta['product_categories']), 'excluded_product_categories' => Projection::ids($meta['exclude_product_categories']),
                'allowed_email_count' => Projection::emailCount($meta['customer_email']),
                'individual_use' => $meta['individual_use'] === 'yes', 'free_shipping' => $meta['free_shipping'] === 'yes',
                'exclude_sale_items' => $meta['exclude_sale_items'] === 'yes',
                'minimum_amount' => Projection::decimal($meta['minimum_amount']), 'maximum_amount' => Projection::decimal($meta['maximum_amount']),
                'recurring_on_renewals' => Projection::recurring($typeValue),
                'renewal_payment_limit' => Projection::number($meta['_wcs_number_payments'] === '' ? '0' : $meta['_wcs_number_payments']),
                'subscriptions' => $subscriptions, 'orders_12_months' => (int) $orderCount];
            $codes[] = $row;
            if ($expiry !== null && $expiry < $now->format('Y-m-d\TH:i:s\Z')) {
                $expired[] = $code;
            }
            if ($count === 0) {
                $never[] = $code;
            }
        }
        $currency = $this->option('woocommerce_currency');
        return ['schema' => 'imagine-a10-coupons-v1', 'read_only' => true, 'generated_at_utc' => $now->format('Y-m-d\TH:i:s\Z'),
            'storage' => $hpos ? 'hpos' : 'classic', 'currency' => preg_match('/\A[A-Z]{3}\z/D', $currency) ? $currency : null,
            'window' => ['from_utc' => str_replace(' ', 'T', $cutoff) . 'Z', 'to_utc' => $now->format('Y-m-d\TH:i:s\Z'), 'inclusive' => true],
            'codes' => $codes, 'expired' => $expired, 'never_used' => $never,
            'limitations' => [
                'Reglages enregistres uniquement, aucun bootstrap ni filtre tiers; aucune promesse de remise effective future.',
                'Recurrence standard Subscriptions; null pour type inconnu. Limite renouvellements: 0 illimitee; ce total configure ne mesure pas le solde de chaque abonnement.',
                'Commandes distinctes par code et creation UTC sur douze mois calendaires; tous statuts sauf corbeille et auto-draft, futurs et remboursements enfants exclus. Ce ne sont pas des ventes nettes.',
                'Abonnements porteurs distincts: active, on-hold, pending et pending-cancel separes; cancelled et expired exclus.',
                'Jamais utilise signifie usage_count enregistre egal a zero, pas une reconstruction historique. Expire et jamais utilise peuvent se recouper.',
                'Aucun reclassement ni suppression. Usage limits 0 sans limite, item_limit null sans limite, montants null absents ou non numeriques.',
                'Site simple, configuration litterale, tables InnoDB, stockage Woo standard; metadonnees coupon dupliquees refusees.',
            ]];
    }
}
