<?php

/**
 * Plugin Name: Imagine — verrou de copie staging
 * Description: Bloque les sorties, paiements et ordonnanceurs. Ne constitue pas un pare-feu.
 */

declare(strict_types=1);

namespace Imagine\Staging;

if (!defined('ABSPATH')) { // Le banc unitaire définit son faux environnement explicitement.
    if (!function_exists('wp_get_environment_type')) {
        exit(78);
    }
}
if (wp_get_environment_type() !== 'staging') {
    http_response_code(503);
    exit(78);
}
if (!defined('WP_ENVIRONMENT_TYPE')) {
    define('WP_ENVIRONMENT_TYPE', 'staging');
}
if (WP_ENVIRONMENT_TYPE !== 'staging' || wp_get_environment_type() !== 'staging'
    || (defined('DISABLE_WP_CRON') && DISABLE_WP_CRON !== true)) {
    http_response_code(503);
    exit(78);
}
if (!defined('DISABLE_WP_CRON')) {
    define('DISABLE_WP_CRON', true);
}
if (!defined('WP_HTTP_BLOCK_EXTERNAL')) {
    define('WP_HTTP_BLOCK_EXTERNAL', true);
}
if (!defined('DISALLOW_FILE_EDIT')) {
    define('DISALLOW_FILE_EDIT', true);
}

add_filter('pre_wp_mail', static fn (): bool => false, PHP_INT_MAX);
add_filter('pre_http_request', static fn (): \WP_Error => new \WP_Error('imagine_staging_offline', 'Sortie réseau interdite sur cette copie.'), PHP_INT_MAX);
add_filter('pre_option_blog_public', static fn (): string => '0', PHP_INT_MAX);
add_filter('wp_robots', static fn (): array => ['noindex' => true, 'nofollow' => true], PHP_INT_MAX);
add_filter('woocommerce_subscriptions_is_duplicate_site', static fn (): bool => true, PHP_INT_MAX);
add_filter('woocommerce_available_payment_gateways', static fn (): array => [], PHP_INT_MAX);
add_filter('action_scheduler_allow_async_request_runner', static fn (): bool => false, PHP_INT_MAX);
add_filter('pre_schedule_event', static fn (): bool => false, PHP_INT_MAX);
add_filter('pre_reschedule_event', static fn (): bool => false, PHP_INT_MAX);
add_filter('pre_get_ready_cron_jobs', static fn (): array => [], PHP_INT_MAX);
add_action('action_scheduler_before_execute', static function (): never {
    throw new \LogicException('IMAGINE_STAGING_EXECUTION_INTERDITE');
}, PHP_INT_MIN);
add_action('init', static function (): void {
    remove_all_actions('action_scheduler_run_queue');
}, PHP_INT_MAX);
if (defined('DOING_CRON') && DOING_CRON) {
    http_response_code(503);
    exit(78);
}
