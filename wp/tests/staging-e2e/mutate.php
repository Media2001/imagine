<?php

declare(strict_types=1);

namespace Imagine\E2E;

if (!defined('ABSPATH') || wp_get_environment_type() !== 'staging') {
    throw new \RuntimeException('Isolated synthetic fixture only');
}
add_filter('pre_wp_mail', '__return_true', PHP_INT_MAX); // One process only.
$case = getenv('E2E_MUTATION') ?: 'all';
$fixture = get_option('imagine_e2e_fixture');
$userId = (int) $fixture['users'][1];
$order = wc_get_order((int) $fixture['orders'][0]);
$run = static function (string $name, callable $mutate) use ($case): void {
    if ($case === $name || $case === 'all' || ($case === 'supported' && $name !== 'form-email')) {
        $mutate();
    }
};
$run('service-key', static function (): void {
    update_option('imagine_e2e_hidden_trap', ['nested' => ['value' => 'sk_live_SYNTHETIC_E2E_NOT_A_KEY_00000000']]);
    update_option('woocommerce_stripe_settings', ['enabled' => 'yes', 'testmode' => 'no',
        'secret_key' => 'sk_live_SYNTHETIC_E2E_NOT_A_KEY_00000000',
        'publishable_key' => 'pk_live_SYNTHETIC_E2E_NOT_A_KEY_00000000',
        'restricted_key' => 'rk_live_SYNTHETIC_E2E_NOT_A_KEY_00000000',
        'webhook_secret' => 'whsec_SYNTHETIC_E2E_NOT_A_KEY_00000000']);
    update_option('sib_api_key', 'xkeysib-SYNTHETIC_E2E_NOT_A_KEY_00000000');
    update_option('wp_mail_smtp', ['mail' => ['from_email' => 'smtp-fictif@invalid.example'],
        'smtp' => ['host' => 'smtp.invalid.example', 'user' => 'SYNTHETIC-NOT-A-LOGIN', 'pass' => 'SYNTHETIC-NOT-A-PASSWORD']]);
});
$run('user-token', static function () use ($userId): void {
    foreach (['_stripe_customer_id' => 'cus_SYNTHETICE2E00000', '_stripe_source_id' => 'src_SYNTHETICE2E00000',
        '_stripe_payment_method' => 'pm_SYNTHETICE2E00000', '_stripe_setup_intent' => 'seti_SYNTHETICE2E00000'] as $key => $value) {
        update_user_meta($userId, $key, $value);
    }
    $token = new \WC_Payment_Token_CC();
    $token->set_token('pm_SYNTHETICE2E00000');
    $token->set_gateway_id('stripe');
    $token->set_user_id($userId);
    $token->set_last4('0000');
    $token->set_expiry_month('12');
    $token->set_expiry_year('2099');
    $token->set_card_type('synthetic');
    $token->save();
});
$run('order-token', static function () use ($order): void {
    foreach (['_stripe_customer_id' => 'cus_SYNTHETICE2EORDER', '_stripe_source_id' => 'src_SYNTHETICE2EORDER',
        '_stripe_payment_method' => 'pm_SYNTHETICE2EORDER', '_stripe_setup_intent' => 'seti_SYNTHETICE2EORDER'] as $key => $value) {
        $order->update_meta_data($key, $value);
    }
    $order->save();
});
$run('paypal', static function () use ($userId, $order): void {
    update_user_meta($userId, '_paypal_billing_agreement_id', 'B-SYNTHETIC-E2E-NOT-A-TOKEN');
    $order->update_meta_data('_paypal_subscription_id', 'I-SYNTHETIC-E2E-NOT-A-TOKEN');
    $order->save();
    update_option('woocommerce_paypal_settings', ['enabled' => 'yes', 'testmode' => 'no',
        'api_username' => 'SYNTHETIC-E2E-NOT-A-LOGIN', 'api_password' => 'SYNTHETIC-E2E-NOT-A-PASSWORD',
        'api_signature' => 'SYNTHETIC-E2E-NOT-A-SIGNATURE']);
});
$run('user-email', static function () use ($userId): void {
    wp_update_user(['ID' => $userId, 'user_email' => 'personnage-fictif@invalid.example']);
});
$run('order-email', static function () use ($order): void {
    $order->set_billing_email('commande-fictive@invalid.example');
    $order->save();
});
$run('note-email', static function () use ($order): void {
    $order->add_order_note('Personnage inventé: note-fictive@invalid.example ; IP de documentation 192.0.2.123.');
});
$run('form-email', static function (): void {
    wp_insert_post(['post_type' => 'imagine_e2e_form', 'post_status' => 'private',
        'post_title' => 'Formulaire enregistré fictif E2E',
        'post_content' => 'Formulaire inventé: formulaire-fictif@invalid.example ; 192.0.2.123.']);
});
$run('scheduled-outbound', static function (): void {
    if (!function_exists('as_schedule_single_action')) {
        throw new \RuntimeException('Real Woo Action Scheduler dependency missing');
    }
    as_schedule_single_action(time() + 86400, 'imagine_e2e_outbound',
        ['recipient' => 'action-fictive@invalid.example', 'url' => 'https://webhook.invalid.example'], 'imagine-e2e');
    wp_schedule_single_event(time() + 86400, 'imagine_e2e_outbound_cron', ['action-fictive@invalid.example']);
    $webhook = new \WC_Webhook();
    $webhook->set_name('Webhook inventé E2E');
    $webhook->set_topic('order.updated');
    $webhook->set_delivery_url('https://webhook.invalid.example');
    $webhook->set_secret('SYNTHETIC-NOT-A-WEBHOOK-SECRET');
    $webhook->set_status('active');
    $webhook->save();
});
echo 'E2E_MUTATION_APPLIED ' . $case . "\n";
