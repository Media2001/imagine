<?php

declare(strict_types=1);

namespace Imagine\E2E;

if (!defined('ABSPATH') || wp_get_environment_type() !== 'staging') {
    throw new \RuntimeException('Isolated synthetic fixture required');
}
global $wpdb;
$phase = getenv('E2E_ORACLE_PHASE') ?: 'fixture';
$hits = [];
$tables = $wpdb->get_col('SHOW TABLES');
foreach ($tables as $table) {
    $quoted = '`' . str_replace('`', '``', $table) . '`';
    $columns = $wpdb->get_results('SHOW COLUMNS FROM ' . $quoted);
    foreach ($columns as $column) {
        if (!preg_match('/char|text|blob|json|enum|set/i', $column->Type)) {
            continue;
        }
        $columnQuoted = '`' . str_replace('`', '``', $column->Field) . '`';
        foreach ($wpdb->get_col('SELECT ' . $columnQuoted . ' FROM ' . $quoted) as $value) {
            if (!is_string($value)) {
                continue;
            }
            $kinds = [];
            if (preg_match('/(?:sk_live_|pk_live_|rk_live_|whsec_|xkeysib-)[A-Za-z0-9_-]+/', $value)) {
                $kinds[] = 'service-key';
            }
            if (preg_match('/(?:cus_|pm_|src_|seti_)[A-Za-z0-9]+/', $value)) {
                $kinds[] = 'payment-identifier';
            }
            if (preg_match('/[BI]-SYNTHETIC-E2E-NOT-A-TOKEN/', $value)) {
                $kinds[] = 'paypal-identifier';
            }
            if (preg_match('/[A-Z0-9._%+-]+@invalid\.example\b/i', $value)) {
                $kinds[] = 'invented-offdomain-email';
            }
            if ($phase === 'after' && str_contains($value, '192.0.2.123')) {
                $kinds[] = 'invented-documentation-ip';
            }
            foreach ($kinds as $kind) {
                $key = $table . '.' . $column->Field . ':' . $kind;
                $hits[$key] = ($hits[$key] ?? 0) + 1;
            }
        }
    }
}
$badUserEmails = (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->users} WHERE user_email NOT REGEXP '^[^@]+@example[.]org$'");
$badOrderEmails = 0;
foreach (wc_get_orders(['limit' => -1, 'type' => 'shop_order']) as $order) {
    if (!preg_match('/^[^@]+@example\.org$/D', $order->get_billing_email())) {
        ++$badOrderEmails;
    }
}
$pendingOutbound = 0;
if (in_array($wpdb->prefix . 'actionscheduler_actions', $tables, true)) {
    $pendingOutbound = (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}actionscheduler_actions WHERE status='pending' AND hook='imagine_e2e_outbound'");
}
$cronOutbound = 0;
foreach (_get_cron_array() as $hooks) {
    $cronOutbound += isset($hooks['imagine_e2e_outbound_cron']) ? 1 : 0;
}
$webhooks = in_array($wpdb->prefix . 'wc_webhooks', $tables, true)
    ? (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wc_webhooks WHERE status='active'") : 0;
$tokens = in_array($wpdb->prefix . 'woocommerce_payment_tokens', $tables, true)
    ? (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}woocommerce_payment_tokens") : 0;
$result = ['residue_hits' => $hits, 'bad_user_emails' => $badUserEmails,
    'bad_order_emails' => $badOrderEmails, 'pending_outbound' => $pendingOutbound,
    'cron_outbound' => $cronOutbound, 'active_webhooks' => $webhooks, 'payment_tokens' => $tokens,
    'user_count' => (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->users}"),
    'order_count' => count(wc_get_orders(['limit' => -1, 'return' => 'ids', 'type' => 'shop_order'])),
    'sessions' => (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->usermeta} WHERE meta_key='session_tokens'"),
    'blog_public' => get_option('blog_public'), 'environment' => wp_get_environment_type(),
    'home' => get_option('home'), 'siteurl' => get_option('siteurl')];
if ($phase === 'after' || $phase === 'mail') {
    require_once ABSPATH . WPINC . '/PHPMailer/Exception.php';
    require_once ABSPATH . WPINC . '/PHPMailer/PHPMailer.php';
    require_once ABSPATH . WPINC . '/PHPMailer/SMTP.php';
    require_once ABSPATH . WPINC . '/class-wp-phpmailer.php';
    $spy = new class(true) extends \WP_PHPMailer {
        public int $e2eCalls = 0;
        public function send()
        {
            ++$this->e2eCalls;
            return true; // Never actually connects or launches sendmail.
        }
    };
    $GLOBALS['phpmailer'] = $spy;
    $result['wp_mail_return'] = wp_mail('probe@example.org', 'E2E_ONLY', 'Synthetic non-delivered mail probe');
    $result['mail_dispatch_calls'] = $spy->e2eCalls;
}
echo 'E2E_JSON=' . wp_json_encode($result) . "\n";
