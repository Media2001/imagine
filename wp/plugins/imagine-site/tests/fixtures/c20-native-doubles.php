<?php

declare(strict_types=1);

// Doubles of native inputs only. No access decision/rule is reproduced here.
class WP_Post
{
    public int $ID = 1;
    public string $post_type = 'imagine_numero';
    public string $post_status = 'publish';
}
class WC_Subscription
{
    public string $status = 'pending-cancel';
    public string $end = '2026-12-25 18:01:50';
    public string $method = 'bacs';
    public string $period = 'year';
    public int $interval = 1;
    public bool $manual = true;
    public function get_date($key, $zone = 'gmt') { return $key === 'end' ? $this->end : '2026-01-01 00:00:00'; }
    public function get_customer_id() { return 700; }
    public function get_status() { return $this->status; }
    public function get_requires_manual_renewal() { return $this->manual; }
    public function get_payment_method() { return $this->method; }
    public function get_billing_period() { return $this->period; }
    public function get_billing_interval() { return $this->interval; }
    public function get_meta($key) { return ''; }
}
class C20MembershipDouble
{
    public string $end = '2027-01-01 00:00:00';
    public function get_plan_id() { return 10; }
    public function get_user_id() { return 700; }
    public function get_id() { return 20; }
    public function get_start_date() { return '2026-01-01 00:00:00'; }
    public function get_end_date($format, $adjust) { return $this->end; }
    public function get_status() { return 'pending'; }
}
function get_current_user_id() { return 700; }
function get_userdata($id) { return (object) ['roles' => ['subscriber']]; }
function get_option($key, $default = false) { return $key === 'imagine_acces_plans' ? [10 => 'abonnement'] : $default; }
function get_post_meta($id, $key, $single) { return $key === '_subscription_id' ? 30 : '2026-01-01'; }
function wp_timezone() { return new DateTimeZone('UTC'); }
function wc_memberships_get_user_memberships($id, $args) { return [$GLOBALS['c20_membership']]; }
function wcs_get_subscription($id) { return $GLOBALS['c20_subscription']; }
function wc_memberships() {
    return new class {
        public function get_integrations_instance() { return $this; }
        public function get_subscriptions_instance() { return $this; }
        public function get_subscription_from_membership($id) { return $GLOBALS['c20_subscription']; }
    };
}
function wp_get_environment_type() { return 'local'; }
function home_url() { return 'http://192.168.129.32:8085'; }
function __($text, $domain) { $GLOBALS['c20_translations'][] = [$text, $domain]; return '<em>' . $text . '</em>'; }
function esc_html($text) { return htmlspecialchars($text, ENT_QUOTES, 'UTF-8'); }
function esc_attr($text) { return esc_html($text); }
function esc_html__($text, $domain) { return esc_html(__($text, $domain)); }
function wp_date($format, $time, $zone) { return gmdate($format, $time); }
