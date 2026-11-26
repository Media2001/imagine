<?php

declare(strict_types=1);

namespace Imagine\Contacts;

/** Only the existing A11 runtime; never execute wp-config or open a second connection. */
final class Accounts
{
    public static function collect(string $site): array
    {
        \Imagine\PublicAddresses\Runtime::boot($site);
        global $wpdb;
        $engines = $wpdb->get_col("SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE='BASE TABLE'");
        if (array_filter($engines, static fn($engine): bool => $engine !== 'InnoDB')) {
            throw new \RuntimeException('A14_TRANSACTIONAL_TABLES_REQUIRED');
        }
        $storage = get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic';
        $active = $storage === 'hpos'
            ? $wpdb->get_col("SELECT DISTINCT customer_id FROM {$wpdb->prefix}wc_orders WHERE type='shop_subscription' AND status='wc-active'")
            : $wpdb->get_col("SELECT DISTINCT m.meta_value FROM {$wpdb->posts} p JOIN {$wpdb->postmeta} m ON m.post_id=p.ID AND m.meta_key='_customer_user' WHERE p.post_type='shop_subscription' AND p.post_status='wc-active' AND m.meta_id=(SELECT MIN(x.meta_id) FROM {$wpdb->postmeta} x WHERE x.post_id=p.ID AND x.meta_key='_customer_user')");
        $accounts = [];
        foreach ($wpdb->get_results("SELECT ID,user_email FROM {$wpdb->users} ORDER BY ID", ARRAY_A) as $row) {
            $technical = (bool) $wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key='imagine_sans_email' AND meta_value='1'", $row['ID']));
            $technical = $technical || str_ends_with(Matcher::normalise($row['user_email']), '@sans-email.imagine.invalid');
            $accounts[] = ['email' => $row['user_email'], 'technical' => $technical, 'active' => in_array((string) $row['ID'], $active, true)];
        }
        return ['storage' => $storage, 'accounts' => $accounts];
    }
}
