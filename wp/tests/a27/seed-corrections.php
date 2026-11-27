<?php

declare(strict_types=1);

// Parent's disposable fictitious fixture only; never loaded by the audit tool.
add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
require_once '/subject/a19/Inventory.php';
$case = getenv('A27_CORRECTION_CASE');
if (!in_array($case, ['opaque', 'conflict', 'reference-only', 'unique'], true)) {
    throw new RuntimeException('A27_SEED_CORRECTION_CASE');
}
global $wpdb;
foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $sub) {
    $sub->delete(true);
}
$wpdb->query("DELETE FROM {$wpdb->prefix}woocommerce_payment_tokenmeta");
$wpdb->query("DELETE FROM {$wpdb->prefix}woocommerce_payment_tokens");
$opaqueSchema = static function ($schema, $sub) {
    if ($sub->get_payment_method('edit') === 'ppcp-gateway') {
        $schema['ppcp-gateway']['post_meta']['a27_opaque'] = [
            'value' => $sub->get_meta('_imagine_a27_opaque', true, 'edit')];
    }
    return $schema;
};
add_filter('woocommerce_subscription_payment_meta', $opaqueSchema, 10, 2);
for ($n = 0; $n < 5; $n++) {
    $login = 'a27-correction-' . $case . '-' . $n;
    $existing = get_user_by('login', $login);
    $user = $existing ? $existing->ID : wp_insert_user(['user_login' => $login,
        'user_email' => $login . '@example.org', 'user_pass' => wp_generate_password(40)]);
    if (is_wp_error($user)) {
        throw new RuntimeException('A27_SEED_CORRECTION_ACCOUNT');
    }
    $sub = wcs_create_subscription(['customer_id' => (int) $user, 'status' => 'pending',
        'billing_period' => 'month', 'billing_interval' => 1]);
    if (is_wp_error($sub)) {
        throw new RuntimeException('A27_SEED_CORRECTION_SUBSCRIPTION');
    }
    $sub->set_payment_method($case === 'opaque' ? 'ppcp-gateway' : 'stripe_sepa');
    $sub->set_requires_manual_renewal(false);
    if ($case === 'opaque') {
        $sub->update_meta_data('_imagine_a27_opaque', ['value' => 'A27_OPAQUE_PRIVATE_CANARY_' . $n]);
    } else {
        $value = 'A27_CORRECTION_REFERENCE_PRIVATE_CANARY_' . $n;
        $sub->update_meta_data('_stripe_source_id', $value);
        if ($case !== 'reference-only') {
            $linked = null;
            foreach (['A', 'B'] as $label) {
                $token = new WC_Payment_Token_eCheck();
                $token->set_user_id((int) $user);
                $token->set_gateway_id('stripe_sepa');
                $token->set_token($label === 'A' ? $value : 'A27_OTHER_PRIVATE_CANARY_' . $n);
                $token->set_last4('4242');
                if (!$token->save()) {
                    throw new RuntimeException('A27_SEED_CORRECTION_TOKEN');
                }
                if ($label === ($case === 'unique' ? 'A' : 'B')) {
                    $linked = $token;
                }
            }
        }
    }
    $sub->save();
    if ($case === 'conflict' || $case === 'unique') {
        $sub->add_payment_token($linked);
    }
    $sub->update_status('active');
    $stored = wcs_get_subscription($sub->get_id());
    if ($stored->get_status('edit') !== 'active' || $stored->get_requires_manual_renewal('edit')) {
        throw new RuntimeException('A27_SEED_CORRECTION_STATE');
    }
    if ($case === 'opaque' && ($stored->get_payment_tokens() !== []
        || !is_array($stored->get_meta('_imagine_a27_opaque', true, 'edit'))
        || \Imagine\SubscriptionCoherence\Inventory::paymentReference($stored) !== 'absent')) {
        throw new RuntimeException('A27_SEED_ACTUAL_A19_BOUNDARY');
    }
}
echo "A27_CORRECTION_SEED_OK\n";
