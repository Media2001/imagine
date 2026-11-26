<?php

declare(strict_types=1);

final class A23RoleDatabaseDouble
{
    public string $prefix = 'wp_';
    public string $last_error = '';
    public string $storage = 'classic';
    public array $users = [];
    public array $commerce = [];

    // phpcs:ignore PSR1.Methods.CamelCapsMethodName.NotCamelCaps -- WordPress wpdb API compatibility.
    public function get_results(string $sql, string $format): array
    {
        if (str_contains($sql, 'woocommerce_custom_orders_table_enabled')) {
            return [['option_value' => $this->storage === 'hpos' ? 'yes' : 'no']];
        }
        if (str_contains($sql, 'imagine_staging_disabled_plugins')) {
            return [];
        }
        if (str_contains($sql, '`wp_users`')) {
            return $this->users;
        }
        if (str_contains($sql, '`wp_posts`') || str_contains($sql, '`wp_wc_orders`')) {
            return $this->commerce;
        }
        throw new \RuntimeException('A23_TEST_UNEXPECTED_QUERY');
    }
}
