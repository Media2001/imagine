<?php

/** Command-scoped guard, loaded by WP-CLI before WordPress. */

declare(strict_types=1);

namespace Imagine\Bascule;

if (!defined('WP_CLI') || WP_CLI !== true) {
    exit(78);
}
$imagineA04Site = getenv('IMAGINE_A04_SITE');
if (!is_string($imagineA04Site) || !is_dir($imagineA04Site)) {
    exit(78);
}
require_once $imagineA04Site . '/wp-includes/plugin.php';
unset($imagineA04Site);
add_filter('pre_wp_mail', static fn(): bool => false, PHP_INT_MAX);
add_filter('pre_http_request', static fn() => new \WP_Error('imagine_a04_offline', 'Sortie bloquée pendant la bascule.'), PHP_INT_MAX);
add_filter('woocommerce_available_payment_gateways', static fn(): array => [], PHP_INT_MAX);
add_filter('woocommerce_subscriptions_is_duplicate_site', static fn (): bool => true, PHP_INT_MAX);
// Keep Woo migrations inside its own explicit, journalled stage.
add_filter('woocommerce_enable_auto_update_db', static fn (): bool => false, PHP_INT_MAX);
add_filter('action_scheduler_allow_async_request_runner', static fn(): bool => false, PHP_INT_MAX);
add_filter('pre_get_ready_cron_jobs', static fn(): array => [], PHP_INT_MAX);
add_filter('pre_schedule_event', static fn(): bool => false, PHP_INT_MAX);
add_filter('pre_reschedule_event', static fn(): bool => false, PHP_INT_MAX);
add_action('action_scheduler_before_execute', static function (): never {
    throw new \LogicException('A04_GLOBAL_QUEUE_FORBIDDEN');
}, PHP_INT_MIN);
add_action('init', static function (): void {
    remove_all_actions('action_scheduler_run_queue');
}, PHP_INT_MAX);
