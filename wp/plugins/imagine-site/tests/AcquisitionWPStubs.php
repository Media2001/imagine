<?php

declare(strict_types=1);

namespace {
    final class WP_Error
    {
        public function __construct(public string $code = '', public string $message = '') {}
    }
    final class WC_Order
    {
        public function __construct(public int $owner = 28, public bool $paid = true, public bool $dated = true, public string $via = 'checkout') {}
        public function get_type(): string { return 'shop_order'; }
        public function get_customer_id(): int { return $this->owner; }
        public function is_paid(): bool { return $this->paid; }
        public function get_date_paid(): ?int { return $this->dated ? 100 : null; }
        public function get_created_via(): string { return $this->via; }
    }
}

namespace Imagine\Site {
    const DB_NAME = 'fictif';
    function wc_get_order(int $id): mixed { return $GLOBALS['c27_orders'][$id] ?? false; }
    function get_option(string $key, mixed $default = false): mixed { return $GLOBALS['c27_options'][$key] ?? $default; }
    function add_option(string $key, mixed $value, string $unused = '', bool $autoload = true): bool
    {
        if (isset($GLOBALS['c27_options'][$key])) { return false; }
        $GLOBALS['c27_options'][$key] = $value;
        return true;
    }
    function update_option(string $key, mixed $value, bool $autoload = true): bool { $GLOBALS['c27_options'][$key] = $value; return true; }
    function delete_option(string $key): bool { unset($GLOBALS['c27_options'][$key]); return true; }
    function get_user_meta(int $id, string $key, bool $single): mixed { return $GLOBALS['c27_meta'][$id][$key] ?? ''; }
    function update_user_meta(int $id, string $key, mixed $value): bool
    {
        // WordPress déséchappe réellement les métadonnées, contrairement aux options.
        $GLOBALS['c27_meta'][$id][$key] = wp_unslash($value);
        return true;
    }
    function delete_user_meta(int $id, string $key): bool { unset($GLOBALS['c27_meta'][$id][$key]); return true; }
    function wp_slash(mixed $value): mixed { return is_array($value) ? array_map(__NAMESPACE__ . '\\wp_slash', $value) : (is_string($value) ? addslashes($value) : $value); }
    function wp_unslash(mixed $value): mixed { return is_array($value) ? array_map(__NAMESPACE__ . '\\wp_unslash', $value) : (is_string($value) ? stripslashes($value) : $value); }
    function wp_cache_delete(mixed $key, string $group): void {}
    function is_wp_error(mixed $value): bool { return $value instanceof \WP_Error; }
    function __(string $text, string $domain = ''): string { return $text; }
    function is_email(string $email): bool { return str_ends_with($email, '@example.org'); }
    function get_user_by(string $field, string $email): object|false
    {
        global $wpdb;
        if (!empty($GLOBALS['c27_user_sql_fail'])) { $wpdb->last_error = 'lecture fictive refusée'; return false; }
        return (object) ['ID' => $email === 'tiers@example.org' ? 29 : 28];
    }
    function wp_json_encode(mixed $value, int $flags = 0): string { return json_encode($value, $flags); }
    function maybe_unserialize(string $value): mixed { return unserialize($value); }
    function add_settings_error(string $key, string $code, string $message): void { $GLOBALS['c27_errors'][] = $code; }
}
