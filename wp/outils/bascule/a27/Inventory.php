<?php

declare(strict_types=1);

namespace Imagine\SavedPayments;

final class Inventory
{
    private const REFERENCES = [
        'stripe' => ['_stripe_source_id', '_stripe_card_id'],
        'stripe_sepa' => ['_stripe_source_id', '_stripe_card_id'],
        'paypal' => ['_paypal_subscription_id'],
    ];

    private static function select(string $sql): array
    {
        global $wpdb;
        $rows = $wpdb->get_results($sql, ARRAY_A);
        if (!is_array($rows) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A27_QUERY_FAILED');
        }
        return $rows;
    }

    public static function collect(string $site, string $audit): array
    {
        Analysis::clock($audit);
        foreach (['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
            'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook) {
            $GLOBALS['wp_filter'][$hook][PHP_INT_MAX][] = ['function' => static fn(): int => 0, 'accepted_args' => 0];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        if (!function_exists('wcs_get_subscriptions') || !class_exists(\WC_Payment_Tokens::class)) {
            throw new \RuntimeException('A27_NATIVE_API_UNAVAILABLE');
        }
        global $wpdb;
        $p = $wpdb->prefix;
        $storage = \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled() ? 'hpos' : 'classic';
        $neutralised = (bool) self::select("SELECT option_id FROM `{$p}options`"
            . " WHERE option_name='imagine_staging_disabled_plugins'");
        $subscriptions = [];
        $tokens = [];
        if (!$neutralised) {
            // Native schemas may be supplied by installed gateway constructors. No charge handler is called.
            WC()->payment_gateways();
            // Native get_customer_tokens() can limit the page; enumerate ALL raw IDs first.
            $rows = self::select("SELECT token_id,user_id,gateway_id,type,token FROM `{$p}woocommerce_payment_tokens` ORDER BY token_id");
            foreach ($rows as $row) {
                $id = (int) $row['token_id'];
                $token = \WC_Payment_Tokens::get($id);
                $readable = $token instanceof \WC_Payment_Token;
                $user = (int) $row['user_id'];
                $tokens[] = ['id' => $id, 'user' => $user, 'account' => $user > 0 && get_userdata($user) !== false,
                    'gateway' => (string) $row['gateway_id'], 'value' => (string) $row['token'],
                    'type' => $readable ? (string) $token->get_type() : '', 'readable' => $readable,
                    'year' => $token instanceof \WC_Payment_Token_CC ? (string) $token->get_expiry_year() : '',
                    'month' => $token instanceof \WC_Payment_Token_CC ? (string) $token->get_expiry_month() : ''];
            }
            foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1,
                'subscription_status' => Analysis::LIVE]) as $sub) {
                if (!$sub instanceof \WC_Subscription) {
                    throw new \RuntimeException('A27_DATA_UNSUPPORTED');
                }
                $gateway = $sub->get_payment_method('edit');
                $meta = [];
                foreach (self::REFERENCES[$gateway] ?? [] as $key) {
                    $value = $sub->get_meta($key, true, 'edit');
                    if ($value !== '') {
                        // Stripe reads source first, with the legacy card key as fallback.
                        $meta[$key] = $value;
                        break;
                    }
                }
                $subscriptions[] = ['user' => (int) $sub->get_customer_id('edit'),
                    'status' => $sub->get_status('edit'), 'gateway' => $gateway,
                    'manual' => (bool) $sub->get_requires_manual_renewal('edit'),
                    'tokens' => array_map('intval', $sub->get_payment_tokens()), 'metadata' => $meta,
                    'reference' => \Imagine\SubscriptionCoherence\Inventory::paymentReference($sub)];
            }
        }
        return ['schema' => 'imagine-a27-saved-payments-v1', 'read_only' => true, 'storage' => $storage,
            'neutralisation' => $neutralised ? Analysis::UNKNOWN : 'observe',
            'counts' => Analysis::analyse($subscriptions, $tokens, $audit, $neutralised), 'as_of_utc' => $audit];
    }
}
