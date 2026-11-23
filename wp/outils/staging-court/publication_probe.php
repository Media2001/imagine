<?php

declare(strict_types=1);

// Streamed after the trusted native runtime-probe.php; no endpoint/agent used.
namespace Imagine\Staging;

require '/var/www/html/wp-load.php';
$runtime = runtimeProbe();
$required = ['mail_blocked', 'http_blocked', 'environment_staging', 'cron_disabled',
    'as_async_disabled', 'as_runner_disabled', 'gateways_disabled'];
$ok = true;
foreach ($required as $key) {
    $ok = $ok && ($runtime[$key] ?? null) === true;
}
if ($runtime['subscriptions_present']) {
    $ok = $ok && $runtime['subscriptions_staging'] === true;
}
$allow = imagineUpdateUrlAllowed('https://api.wordpress.org/core/version-check/1.7/')
    && imagineUpdateUrlAllowed('https://downloads.woocommerce.com/fiction')
    && !imagineUpdateUrlAllowed('https://wordpress.org.evil.invalid/fiction')
    && !imagineUpdateUrlAllowed('http://api.wordpress.org/fiction')
    && !imagineUpdateUrlAllowed('https://api.wordpress.org:444/fiction')
    && apply_filters('http_request_args', ['redirection' => 5])['redirection'] === 0;
$settings = defined('WP_HTTP_BLOCK_EXTERNAL') && WP_HTTP_BLOCK_EXTERNAL === true
    && WP_ACCESSIBLE_HOSTS === '*.wordpress.org,*.woocommerce.com'
    && IMAGINE_STAGING_VERIFIED === true;
global $wpdb;
$appPasswords = (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->usermeta} WHERE meta_key='_application_passwords' AND meta_value NOT IN ('','a:0:{}')");
$novamira = is_dir(WP_PLUGIN_DIR . '/novamira') || is_dir(WP_PLUGIN_DIR . '/novamira-pro');
$pluginList = get_option('active_plugins', []);
$fixture = get_option('a01_paid_fixture');
$fidelity = ['plugins' => $pluginList, 'theme' => get_option('stylesheet')];
$scheduler = ['tested' => false];
if (is_array($fixture)) {
    $business = [];
    foreach ($fixture['subs'] as $id) {
        $s = wcs_get_subscription($id);
        $items = [];
        foreach ($s->get_items() as $item) {
            $items[] = ['product' => $item->get_product_id(), 'quantity' => $item->get_quantity(),
                'subtotal' => $item->get_subtotal(), 'total' => $item->get_total(), 'taxes' => $item->get_taxes()];
        }
        $business[] = ['id' => $s->get_id(), 'status' => $s->get_status(), 'customer' => $s->get_customer_id(),
            'interval' => $s->get_billing_interval(), 'period' => $s->get_billing_period(),
            'start' => $s->get_date('start'), 'next' => $s->get_date('next_payment'), 'end' => $s->get_date('end'),
            'currency' => $s->get_currency(), 'total' => $s->get_total(), 'method' => $s->get_payment_method(),
            'billing_country' => $s->get_billing_country(), 'shipping_country' => $s->get_shipping_country(), 'items' => $items];
    }
    $members = [];
    foreach ($fixture['members'] as $key => $id) {
        $m = wc_memberships_get_user_membership($id);
        $members[$key] = ['id' => $id, 'user' => $m->get_user_id(), 'plan' => $m->get_plan_id(),
            'status' => $m->get_status(), 'start' => $m->get_start_date(), 'end' => $m->get_end_date()];
    }
    $fidelity += ['business' => $business, 'membership' => $members,
        'rules_sha256' => hash('sha256', serialize(get_option('wc_memberships_rules')))];
    $rights = [];
    foreach (array_merge(['guest' => 0], $fixture['users']) as $status => $uid) {
        $rights[$status] = (bool) wc_memberships_user_can($uid, 'view', ['post' => $fixture['post']]);
    }
    $fidelity['rights'] = $rights;
    $fidelity['setting_intact'] = get_option('imagine_publication_setting') === ['layout' => 'fiction', 'quantity' => 7];
    if (!empty($fixture['subs'])) {
        $sub = wcs_get_subscription($fixture['subs'][0]);
        $before = count($sub->get_related_orders('ids', 'renewal'));
        $calls = 0;
        add_action('woocommerce_scheduled_subscription_payment', static function () use (&$calls): void { ++$calls; }, PHP_INT_MIN);
        $id = as_schedule_single_action(time() - 5, 'woocommerce_scheduled_subscription_payment',
            ['subscription_id' => $sub->get_id()], 'imagine-a01-publication-synthetic-only');
        \ActionScheduler::runner()->process_action($id, 'A01-disposable-only');
        $after = count(wcs_get_subscription($sub->get_id())->get_related_orders('ids', 'renewal'));
        $scheduler = ['tested' => true, 'callback_calls' => $calls,
            'status' => \ActionScheduler::store()->get_status($id), 'renewals_before' => $before, 'renewals_after' => $after];
        $ok = $ok && $calls === 0 && $before === $after && $scheduler['status'] === 'failed'
            && $fidelity['setting_intact'];
    } else {
        $scheduler = ['tested' => false, 'reason' => 'Subscriptions absent; 6.9.1 not qualified for this extension'];
        $ok = $ok && $fidelity['setting_intact'];
    }
    if (get_option('imagine_a01_69_fixture') === 'yes') {
        $orders = [];
        foreach (wc_get_orders(['limit' => -1, 'orderby' => 'ID', 'order' => 'ASC', 'type' => 'shop_order']) as $order) {
            $items = [];
            foreach ($order->get_items() as $item) {
                $items[] = ['product' => $item->get_product_id(), 'quantity' => $item->get_quantity(),
                    'total' => $item->get_total(), 'tax' => $item->get_total_tax()];
            }
            $orders[] = ['id' => $order->get_id(), 'status' => $order->get_status(),
                'created' => $order->get_date_created()->getTimestamp(), 'total' => $order->get_total(),
                'currency' => $order->get_currency(), 'payment_method' => $order->get_payment_method(),
                'billing_country' => $order->get_billing_country(), 'shipping_country' => $order->get_shipping_country(),
                'items' => $items];
        }
        $fidelity['orders'] = $orders;
        $fidelity['membership_shortcodes'] = [];
        foreach (array_merge(['guest' => 0], $fixture['users']) as $status => $uid) {
            wp_set_current_user($uid);
            $fidelity['membership_shortcodes'][$status] = str_contains(
                do_shortcode('[wcm_restrict plans="a01-fiction-plan"]A01_PRIVATE_CANARY[/wcm_restrict]'), 'A01_PRIVATE_CANARY');
        }
        $fidelity['public_post_unrestricted'] = !wc_memberships_is_post_content_restricted($fixture['public']);
    }
}
$result = ['ok' => $ok && $allow && $settings && $appPasswords === 0,
    'versions' => ['php' => PHP_VERSION, 'wordpress' => get_bloginfo('version'),
        'woocommerce' => function_exists('WC') ? WC()->version : null,
        'subscriptions' => class_exists('WC_Subscriptions') ? \WC_Subscriptions::$version : null,
        'hpos' => class_exists('Automattic\\WooCommerce\\Utilities\\OrderUtil')
            ? \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled() : null,
        'memberships' => function_exists('wc_memberships') ? wc_memberships()->get_version() : null],
    'runtime' => $runtime, 'update_filter_allow_deny' => $allow, 'constants_exact' => $settings,
    'scheduler' => $scheduler, 'fidelity' => $fidelity,
    'novamira_residuals' => ['plugin_present' => $novamira, 'nonempty_application_password_records' => $appPasswords,
        'created_agent_credentials_valid' => $appPasswords === 0 ? false : null,
        'credential_check_method' => 'No authentication attempted; zero application-password records invalidates the created application-password credentials',
        'dashboard_mcp_metadata_may_be_stale' => true]];
echo 'A01_JSON=' . json_encode($result, JSON_THROW_ON_ERROR) . "\n";
