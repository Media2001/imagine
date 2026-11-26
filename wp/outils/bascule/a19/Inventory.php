<?php

declare(strict_types=1);

namespace Imagine\SubscriptionCoherence;

final class Inventory
{
    public static function paymentReference(\WC_Subscription $subscription): string
    {
        $gateway = $subscription->get_payment_method('edit');
        if ($gateway === '') {
            return 'absent';
        }
        foreach ($subscription->get_payment_tokens() as $id) {
            $token = \WC_Payment_Tokens::get((int) $id);
            if (
                $token && $token->get_gateway_id() === $gateway
                && (int) $token->get_user_id() === (int) $subscription->get_customer_id('edit')
            ) {
                return 'present';
            }
        }
        // Standard gateway-declared storage schema, without is_manual() staging fallback.
        $meta = apply_filters('woocommerce_subscription_payment_meta', [], $subscription);
        $values = [];
        foreach ((is_array($meta[$gateway] ?? null) ? $meta[$gateway] : []) as $fields) {
            if (!is_array($fields)) {
                continue;
            }
            foreach ($fields as $field) {
                if (is_array($field) && array_key_exists('value', $field)) {
                    $values[] = is_scalar($field['value']) && (string) $field['value'] !== '';
                }
            }
        }
        if (!$values) {
            return 'unknown';
        }
        return in_array(false, $values, true) ? 'absent' : 'present';
    }

    public static function collect(string $site, string $asOf): array
    {
        $clock = \DateTimeImmutable::createFromFormat('!Y-m-d\TH:i:s\Z', $asOf, new \DateTimeZone('UTC'));
        if (!$clock || $clock->format('Y-m-d\TH:i:s\Z') !== $asOf) {
            throw new \RuntimeException('A19_CLOCK_INVALID');
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        if (!function_exists('wcs_get_subscriptions') || !function_exists('wc_memberships')) {
            throw new \RuntimeException('A19_NATIVE_API_UNAVAILABLE');
        }
        // Initialize installed gateway schemas, never call a gateway or render a payment form.
        WC()->payment_gateways();
        $subscriptions = [];
        foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $sub) {
            $paid = false;
            foreach ($sub->get_related_orders('all', 'any') as $order) {
                if ($order->get_date_paid('edit') !== null || $order->is_paid()) {
                    $paid = true;
                    break;
                }
            }
            $subscriptions[$sub->get_id()] = [
                'status' => $sub->get_status('edit'), 'user' => (int) $sub->get_customer_id('edit'),
                'manual' => (bool) $sub->get_requires_manual_renewal('edit'),
                'gateway' => $sub->get_payment_method('edit'), 'reference' => self::paymentReference($sub),
                'next' => (int) $sub->get_time('next_payment', 'gmt'), 'paid' => $paid,
            ];
        }
        global $wpdb;
        $memberships = [];
        $rows = $wpdb->get_results(
            "SELECT ID,post_parent,post_author,post_status FROM `{$wpdb->posts}` "
                . "WHERE post_type='wc_user_membership' AND post_status NOT IN ('trash','auto-draft') ORDER BY ID",
            ARRAY_A
        );
        if (!is_array($rows) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A19_QUERY_FAILED');
        }
        foreach ($rows as $row) {
            $id = get_post_meta((int) $row['ID'], '_subscription_id', true);
            $status = str_starts_with($row['post_status'], 'wcm-')
                ? substr($row['post_status'], 4) : $row['post_status'];
            $memberships[] = ['plan' => (int) $row['post_parent'], 'user' => (int) $row['post_author'],
                'status' => $status, 'subscription' => is_numeric($id) ? (int) $id : 0];
        }
        return ['schema' => 'imagine-a19-coherence-v1', 'read_only' => true,
            'storage' => get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic',
            'as_of_utc' => $asOf, 'counts' => Analysis::analyse($subscriptions, $memberships, $clock->getTimestamp()),
            'payment_reference_basis' => 'Reference Woo liee ou champs du schema natif de passerelle ; sinon inconnu.',
            'mode_basis' => 'Drapeau manuel enregistre, pas bascule manuelle effective du staging.',
            'scope' => 'Magasin natif faisant autorite ; liens explicites ; aucun rapprochement par identite.'];
    }
}
