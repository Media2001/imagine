<?php

declare(strict_types=1);

// Oracle-only setup on a fresh fictitious database; never used by the audit.
add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
global $wpdb;
foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $s) {
    $s->delete(true);
}
$wpdb->query("DELETE FROM {$wpdb->prefix}woocommerce_payment_tokenmeta");
$wpdb->query("DELETE FROM {$wpdb->prefix}woocommerce_payment_tokens");
$repetitions = (int) (getenv('A27_REPETITIONS') ?: 1);
if (!in_array($repetitions, [1, 5], true)) {
    throw new RuntimeException('A27_SEED_REPETITIONS');
}
$makeToken = static function (
    int $user,
    string $gateway,
    string $kind,
    string $year,
    string $month,
    string $value
): WC_Payment_Token {
    $token = $kind === 'CC' ? new WC_Payment_Token_CC() : new WC_Payment_Token_eCheck();
    $token->set_user_id($user);
    $token->set_gateway_id($gateway);
    $token->set_token($value);
    $token->set_last4('4242');
    if ($token instanceof WC_Payment_Token_CC) {
        $token->set_card_type('visa');
        $token->set_expiry_year($year);
        $token->set_expiry_month($month);
    }
    if (!$token->save()) {
        throw new RuntimeException('A27_SEED_TOKEN');
    }
    return $token;
};
for ($n = 0; $n < $repetitions; $n++) {
    $users = [];
    for ($i = 0; $i < 7; $i++) {
        $login = 'a27-fictif-' . $repetitions . '-' . $n . '-' . $i;
        $existing = get_user_by('login', $login);
        $user = $existing ? $existing->ID : wp_insert_user(['user_login' => $login,
            'user_email' => $login . '@example.org', 'user_pass' => wp_generate_password(40)]);
        if (is_wp_error($user)) {
            throw new RuntimeException('A27_SEED_ACCOUNT');
        }
        $users[] = (int) $user;
    }
    $nativeTokens = [
        $makeToken($users[0], 'stripe', 'CC', '2027', '03', 'A27_VALID_PRIVATE_CANARY_' . $n),
        $makeToken($users[1], 'stripe', 'CC', '2026', '10', 'A27_EXPIRED_PRIVATE_CANARY_' . $n),
        $makeToken($users[2], 'stripe_sepa', 'eCheck', '', '', 'A27_MANDATE_PRIVATE_CANARY_' . $n),
        null, null,
        $makeToken($users[5], 'stripe', 'CC', '2026', '11', 'A27_REFERENCE_PRIVATE_CANARY_' . $n),
    ];
    $makeToken($users[0], 'stripe', 'eCheck', '', '', 'A27_EXTRA_PRIVATE_CANARY_' . $n);
    $makeToken($users[6], 'stripe', 'CC', '2030', '01', 'A27_ORPHAN_PRIVATE_CANARY_' . $n);
    foreach (['active', 'pending', 'on-hold', 'pending-cancel', 'active', 'active'] as $i => $state) {
        $s = wcs_create_subscription(['customer_id' => $users[$i], 'status' => 'pending',
            'billing_period' => 'month', 'billing_interval' => 1, 'start_date' => '2026-01-01 00:00:00']);
        if (is_wp_error($s)) {
            throw new RuntimeException('A27_SEED_SUBSCRIPTION');
        }
        $gateway = $i === 2 ? 'stripe_sepa' : ($i === 3 ? 'paypal' : 'stripe');
        $s->set_payment_method($gateway);
        $s->set_requires_manual_renewal(false);
        $s->set_billing_first_name('A27_ACCOUNT_PRIVATE_CANARY');
        if ($i === 0) {
            // Exact native metadata match, WITHOUT an order-token link. The old
            // legacy key is stale: native Stripe gives the source key priority.
            $s->update_meta_data('_stripe_source_id', $nativeTokens[$i]->get_token());
            $s->update_meta_data('_stripe_card_id', 'A27_STALE_CARD_PRIVATE_CANARY_' . $n);
        } elseif ($i === 3) {
            $s->update_meta_data('_paypal_subscription_id', 'A27_PAYPAL_PRIVATE_CANARY_' . $n);
        } elseif ($i === 4) {
            $s->update_meta_data('_stripe_source_id', 'A27_UNMATCHED_PRIVATE_CANARY_' . $n);
        }
        $s->save();
        if ($nativeTokens[$i] && $i !== 0) {
            $s->add_payment_token($nativeTokens[$i]);
        }
        if ($i === 0) {
            $reloaded = wcs_get_subscription($s->get_id());
            if ($reloaded->get_payment_tokens() !== []
                || $reloaded->get_meta('_stripe_source_id', true, 'edit') !== $nativeTokens[$i]->get_token()) {
                throw new RuntimeException('A27_SEED_METADATA');
            }
        }
        if ($state !== 'pending') {
            $s->update_status($state);
        }
    }
    foreach ([['active', true], ['cancelled', false]] as [$status, $manual]) {
        $s = wcs_create_subscription(['customer_id' => $users[0], 'status' => 'pending',
            'billing_period' => 'month', 'billing_interval' => 1]);
        $s->set_requires_manual_renewal($manual);
        $s->set_payment_method('stripe');
        $s->save();
        $s->add_payment_token($nativeTokens[0]);
        $s->update_status($status);
    }
}
echo "A27_SEED_OK\n";
