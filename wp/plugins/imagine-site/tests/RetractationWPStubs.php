<?php

declare(strict_types=1);

namespace {
    class WP_Error
    {
        public function __construct(public string $code = '', public string $message = '') {}
        public function get_error_code(): string { return $this->code; }
    }
    class RetractationOrder
    {
        public array $business = ['status' => 'completed', 'total' => '42.00', 'subscription' => 'active', 'access' => true, 'actions' => ['renewal']];
        public array $meta = [];
        public function __construct(public int $id, public int $owner = 7, public bool $subscription = false, public int $parent = 10) {}
        public function get_customer_id(): int { return $this->owner; }
        public function get_id(): int { return $this->id; }
        public function get_type(): string { return $this->subscription ? 'shop_subscription' : 'shop_order'; }
        public function get_parent_id(): int { return $this->parent; }
        public function get_date_paid(): ?DateTimeImmutable { return $GLOBALS['retract_paid'] ? new DateTimeImmutable('2030-01-01 UTC') : null; }
        public function get_meta(string $key): mixed { return $this->meta[$key] ?? ''; }
        public function get_view_order_url(): string { return '/mon-compte/view-order/' . $this->id; }
        public function get_edit_order_url(): string { return '/wp-admin/order/' . $this->id; }
        public function update_meta_data(string $key, mixed $value): void { $this->meta[$key] = $value; }
        public function save_meta_data(): void {}
        public function add_order_note(string $content, bool $customer = false): int
        {
            if ($customer) { $GLOBALS['retract_mail']++; }
            if ($GLOBALS['retract_fail_note']) { return 0; }
            $id = count($GLOBALS['retract_notes']) + 1;
            $GLOBALS['retract_notes'][$id] = ['comment_ID' => $id, 'comment_post_ID' => $this->id, 'comment_content' => $content, 'comment_type' => 'order_note', 'comment_approved' => '1'];
            return $id;
        }
        public function update_status(mixed ...$args): void { $GLOBALS['retract_financial']++; }
        public function save(): void { $GLOBALS['retract_financial']++; }
    }
    class RetractationDB
    {
        public string $comments = 'wp_comments';
        public string $commentmeta = 'wp_commentmeta';
        public string $options = 'wp_options';
        public string $last_error = '';
        public bool $fail = false;
        public bool $locked = false;
        public ?array $snapshot = null;
        public function prepare(string $sql, mixed ...$args): array { return [$sql, $args]; }
        public function get_var(array $query): int
        {
            if (str_contains($query[0], 'GET_LOCK')) { return $this->locked ? 0 : 1; }
            return 1;
        }
        public function query(string|array $query): int|false
        {
            if ($query === 'START TRANSACTION') {
                $this->snapshot = [$GLOBALS['retract_options'], $GLOBALS['retract_notes'], $GLOBALS['retract_meta']];
            } elseif ($query === 'ROLLBACK') {
                [$GLOBALS['retract_options'], $GLOBALS['retract_notes'], $GLOBALS['retract_meta']] = $this->snapshot;
            }
            return 1;
        }
        public function get_results(string|array $query, mixed $mode = null): array
        {
            $this->last_error = $this->fail ? 'Panne SQL fictive' : '';
            if ($this->fail) { return []; }
            $rows = [];
            foreach ($GLOBALS['retract_meta'] as $id => $data) {
                if (isset($GLOBALS['retract_notes'][$id])) { $rows[] = ['comment_id' => $id, 'meta_value' => serialize($data)]; }
            }
            return $rows;
        }
    }
    $GLOBALS['retract_orders'] = [10 => new RetractationOrder(10), 11 => new RetractationOrder(11, 8), 20 => new RetractationOrder(20, 7, true)];
    $GLOBALS['retract_options'] = $GLOBALS['retract_notes'] = $GLOBALS['retract_meta'] = $GLOBALS['retract_hooks'] = [];
    $GLOBALS['retract_mail'] = $GLOBALS['retract_http'] = $GLOBALS['retract_financial'] = 0;
    $GLOBALS['retract_paid'] = true;
    $GLOBALS['retract_fail_note'] = $GLOBALS['retract_fail_journal'] = $GLOBALS['retract_fail_delete'] = false;
    $GLOBALS['retract_now'] = strtotime('2030-01-02 UTC');
    $GLOBALS['wpdb'] = new RetractationDB();
    if (!defined('ARRAY_A')) { define('ARRAY_A', 'ARRAY_A'); }
    function wc_get_order(int $id): ?RetractationOrder { return $GLOBALS['retract_orders'][$id] ?? null; }
    function get_option(string $key, mixed $default = false): mixed { return $GLOBALS['retract_options'][$key] ?? $default; }
    function add_option(string $key, mixed $value, mixed $deprecated = '', mixed $autoload = false): bool
    {
        if (isset($GLOBALS['retract_sanitizers'][$key])) { $value = ($GLOBALS['retract_sanitizers'][$key])($value); }
        if (($GLOBALS['retract_fail_journal'] && str_starts_with($key, 'imagine_reglages_journal_')) || array_key_exists($key, $GLOBALS['retract_options'])) { return false; }
        $GLOBALS['retract_options'][$key] = $value;
        do_action('added_option', $key, $value);
        return true;
    }
    function update_option(string $key, mixed $value, mixed $autoload = false): bool
    {
        if (isset($GLOBALS['retract_sanitizers'][$key])) { $value = ($GLOBALS['retract_sanitizers'][$key])($value); }
        if (!array_key_exists($key, $GLOBALS['retract_options'])) { return add_option($key, $value, '', $autoload); }
        $old = $GLOBALS['retract_options'][$key];
        if ($old === $value) { return false; }
        $GLOBALS['retract_options'][$key] = $value;
        do_action('updated_option', $key, $old, $value);
        return true;
    }
    function delete_option(string $key): bool { unset($GLOBALS['retract_options'][$key]); return true; }
    function do_action(string $hook, mixed ...$args): void { foreach ($GLOBALS['retract_hooks'][$hook] ?? [] as $fn) { $fn(...$args); } }
    function register_setting(string $group, string $key, array $args): void { $GLOBALS['retract_sanitizers'][$key] = $args['sanitize_callback']; }
    function wp_generate_uuid4(): string { return bin2hex(random_bytes(16)); }
    function wp_die(string $message, string $title = '', array $args = []): never { throw new RuntimeException($message); }
    function get_comment(int $id): ?object { return isset($GLOBALS['retract_notes'][$id]) ? (object)$GLOBALS['retract_notes'][$id] : null; }
    function add_comment_meta(int $id, string $key, mixed $value, bool $unique = false): int|false { $GLOBALS['retract_meta'][$id] = wp_unslash($value); return $id; }
    function get_comment_meta(int $id, string $key, bool $single = false): mixed { return $GLOBALS['retract_meta'][$id] ?? ''; }
    function wp_delete_comment(int $id, bool $force = false): bool
    {
        if ($GLOBALS['retract_fail_delete']) { return false; }
        unset($GLOBALS['retract_notes'][$id], $GLOBALS['retract_meta'][$id]);
        return true;
    }
    function wp_cache_delete(mixed ...$args): bool { return true; }
    function clean_comment_cache(mixed ...$args): void {}
    function wp_get_current_user(): object { return (object)['ID' => 7, 'user_login' => 'fictif']; }
    function get_current_user_id(): int { return 7; }
    function get_user_by(string $field, string $email): object|false { return $email === 'fictif@example.org' ? (object)['ID' => 7] : ($email === 'tiers@example.org' ? (object)['ID' => 8] : false); }
    function is_email(string $email): bool { return filter_var($email, FILTER_VALIDATE_EMAIL) !== false; }
    function is_wp_error(mixed $value): bool { return $value instanceof WP_Error; }
    function maybe_unserialize(string $value): mixed { return unserialize($value); }
    function sanitize_textarea_field(string $value): string { return trim(strip_tags($value)); }
    function __(string $value, string $domain): string { return $value; }
    function esc_html__(string $value, string $domain): string { return esc_html($value); }
    function esc_html(string $value): string { return htmlspecialchars($value, ENT_QUOTES, 'UTF-8'); }
    function esc_attr(string $value): string { return esc_html($value); }
    function esc_url(string $value): string { return esc_html($value); }
    function add_action(string $hook, mixed $callback, int $priority = 10, int $args = 1): void { $GLOBALS['retract_hooks'][$hook][] = $callback; }
    function add_filter(string $hook, mixed $callback, int $priority = 10, int $args = 1): void { add_action($hook, $callback); }
    function wp_mail(mixed ...$args): bool { $GLOBALS['retract_mail']++; return false; }
    function wp_remote_get(mixed ...$args): WP_Error { $GLOBALS['retract_http']++; return new WP_Error(); }
    function wp_json_encode(mixed $data, int $flags = 0): string { return json_encode($data, $flags); }
    function wc_get_page_permalink(string $page): string { return '/mon-compte/'; }
    function add_query_arg(mixed $key, mixed $value, string $url): string { return $url . '?c25=' . $value; }
    function wp_nonce_field(string $action, string $key): void { echo '<input name="' . $key . '" value="nonce">'; }
    function wp_create_nonce(string $action): string { return 'nonce'; }
    function wp_verify_nonce(string $nonce, string $action): bool { return $nonce === 'nonce'; }
    function wp_unslash(mixed $value): mixed { return is_array($value) ? array_map('wp_unslash', $value) : (is_string($value) ? stripslashes($value) : $value); }
    function wp_slash(mixed $value): mixed { return is_array($value) ? array_map('wp_slash', $value) : (is_string($value) ? addslashes($value) : $value); }
    function admin_url(string $path = ''): string { return '/wp-admin/' . $path; }
    function current_user_can(string $cap): bool { return true; }
    function add_settings_error(mixed ...$args): void {}
    function selected(mixed $current, mixed $value, bool $echo = true): string { return $current === $value ? ' selected' : ''; }
}
namespace Imagine\Site {
    function time(): int { return $GLOBALS['retract_now']; }
}
