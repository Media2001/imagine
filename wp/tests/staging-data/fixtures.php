<?php

declare(strict_types=1);

use Imagine\Staging\Store;

final class MemoryStore implements Store
{
    public array $tables;
    public bool $ignoreUrlWrites = false;
    public array $columns;
    public array $schemaDetails = [];
    private array $saved = [];
    public function __construct(array $tables, array $columns)
    {
        $this->tables = $tables;
        $this->columns = $columns;
    }
    public function database(): string
    {
        return 'invented_staging';
    }
    public function schema(): array
    {
        return $this->columns;
    }
    public function details(): array
    {
        return $this->schemaDetails;
    }
    public function rows(string $table): array
    {
        return $this->tables[$table] ?? [];
    }
    public function begin(): void
    {
        $this->saved = $this->tables;
    }
    public function commit(): void
    {
        $this->saved = [];
    }
    public function rollback(): void
    {
        $this->tables = $this->saved;
    }
    public function replace(string $table, array $before, ?array $after): void
    {
        if ($this->ignoreUrlWrites && in_array($before['option_name'] ?? '', ['home', 'siteurl'], true)) {
            return;
        }
        foreach ($this->tables[$table] as $i => $row) {
            if ($row === $before) {
                if ($after === null) {
                    unset($this->tables[$table][$i]);
                } else {
                    $this->tables[$table][$i] = $after;
                }
                return;
            }
        }
        throw new RuntimeException('CAS');
    }
    public function insert(string $table, array $row): int
    {
        $key = str_ends_with($table, 'users') ? 'ID' : (str_ends_with($table, 'options') ? 'option_id' : 'umeta_id');
        $id = max(array_merge([0], array_column($this->tables[$table], $key))) + 1;
        $row[$key] = $id;
        $this->tables[$table][] = $row;
        return $id;
    }
}

function fixture(): MemoryStore
{
    $tables = [
        'x_options' => [
            ['option_id' => 1, 'option_name' => 'home', 'option_value' => 'https://invented.test'],
            ['option_id' => 2, 'option_name' => 'siteurl', 'option_value' => 'https://invented.test'],
            ['option_id' => 3, 'option_name' => 'woocommerce_stripe_settings', 'option_value' => serialize(['enabled' => 'yes', 'secret_key' => 'sk_live_SYNTHETIC_ONLY'])],
            ['option_id' => 4, 'option_name' => 'wp_mail_smtp', 'option_value' => serialize(['password' => 'invented'])],
            ['option_id' => 5, 'option_name' => 'cron', 'option_value' => serialize(['invented_external_job'])],
            ['option_id' => 6, 'option_name' => 'x_user_roles', 'option_value' => serialize(['administrator' => ['name' => 'Admin fictif', 'capabilities' => ['read' => true, 'manage_options' => true]]])],
        ],
        'x_users' => [], 'x_usermeta' => [], 'x_posts' => [], 'x_postmeta' => [],
        'x_comments' => [['comment_ID' => 1, 'comment_content' => 'FICTIF subscriber@outside.invalid 192.0.2.1', 'comment_author_email' => 'fictif@outside.invalid', 'comment_author_IP' => '192.0.2.1']],
        'x_actionscheduler_actions' => [['action_id' => 1, 'status' => 'pending', 'hook' => 'invented_outbound', 'args' => '{"email":"synthetic@outside.invalid"}', 'schedule' => 'O:8:"stdClass":0:{}'], ['action_id' => 2, 'status' => 'complete', 'hook' => 'invented', 'args' => '[]', 'schedule' => 'O:8:"stdClass":0:{}']],
        'x_actionscheduler_logs' => [['log_id' => 1, 'message' => 'FICTIF private note']],
        'x_wc_orders' => [], 'x_wc_order_addresses' => [], 'x_wc_orders_meta' => [], 'x_wc_customer_lookup' => [],
        'x_woocommerce_payment_tokens' => [['token_id' => 1, 'token' => 'invented-billing-token']],
        'x_woocommerce_payment_tokenmeta' => [['meta_id' => 1, 'meta_key' => 'brand', 'meta_value' => 'invented']],
    ];
    for ($i = 1; $i <= 30; ++$i) {
        $tables['x_users'][] = ['ID' => $i, 'user_login' => "fictif-$i", 'user_email' => "fictif-$i@outside.invalid", 'user_pass' => 'invented-hash', 'display_name' => 'FICTIF', 'user_nicename' => 'fictif', 'user_url' => 'https://outside.invalid', 'user_activation_key' => 'invented'];
        $tables['x_usermeta'][] = ['umeta_id' => $i, 'user_id' => $i, 'meta_key' => 'billing_country', 'meta_value' => 'BE'];
        $tables['x_usermeta'][] = ['umeta_id' => 1000 + $i, 'user_id' => $i, 'meta_key' => 'first_name', 'meta_value' => 'FICTIF'];
        $tables['x_usermeta'][] = ['umeta_id' => 2000 + $i, 'user_id' => $i, 'meta_key' => 'session_tokens', 'meta_value' => serialize(['SYNTHETIC'])];
        $tables['x_postmeta'][] = ['meta_id' => $i, 'post_id' => $i, 'meta_key' => '_stripe_customer_id', 'meta_value' => 'cus_SYNTHETIC_ONLY'];
        $tables['x_postmeta'][] = ['meta_id' => 1000 + $i, 'post_id' => $i, 'meta_key' => '_billing_address_1', 'meta_value' => 'FICTIF address'];
        $tables['x_postmeta'][] = ['meta_id' => 2000 + $i, 'post_id' => $i, 'meta_key' => '_order_total', 'meta_value' => '42.50'];
        $tables['x_postmeta'][] = ['meta_id' => 3000 + $i, 'post_id' => $i, 'meta_key' => '_payment_method', 'meta_value' => 'stripe'];
        $tables['x_posts'][] = ['ID' => $i, 'post_type' => $i % 2 ? 'shop_order' : 'shop_subscription', 'post_status' => 'wc-active', 'post_title' => 'FICTIF customer', 'post_content' => 'FICTIF address', 'post_excerpt' => 'FICTIF note', 'post_password' => 'invented', 'post_date' => '2026-01-01 00:00:00'];
        $tables['x_wc_orders'][] = ['id' => $i, 'status' => 'wc-active', 'type' => 'shop_order', 'total_amount' => '42.50', 'billing_email' => 'fictif@outside.invalid', 'payment_method' => 'stripe', 'ip_address' => '192.0.2.1', 'user_agent' => 'invented'];
        $tables['x_wc_order_addresses'][] = ['id' => $i, 'order_id' => $i, 'country' => 'BE', 'first_name' => 'FICTIF', 'last_name' => 'FICTIF', 'address_1' => 'FICTIF address', 'email' => 'fictif@outside.invalid', 'phone' => '0000'];
        $tables['x_wc_customer_lookup'][] = ['customer_id' => $i, 'user_id' => $i, 'username' => 'FICTIF', 'first_name' => 'FICTIF', 'last_name' => 'FICTIF', 'email' => 'fictif@outside.invalid', 'country' => 'BE'];
    }
    $columns = [];
    foreach ($tables as $table => $rows) {
        $columns[$table] = $rows ? array_keys($rows[0]) : match ($table) {
            'x_wc_orders_meta' => ['id', 'order_id', 'meta_key', 'meta_value'],
            default => ['umeta_id', 'user_id', 'meta_key', 'meta_value'],
        };
    }
    return new MemoryStore($tables, $columns);
}
