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
$imagine_hosts = defined('IMAGINE_STAGING_VERIFIED') && IMAGINE_STAGING_VERIFIED === true
    ? '*.wordpress.org,*.woocommerce.com' : '';
if (!defined('WP_ACCESSIBLE_HOSTS')) {
    define('WP_ACCESSIBLE_HOSTS', $imagine_hosts);
}
if (WP_HTTP_BLOCK_EXTERNAL !== true || WP_ACCESSIBLE_HOSTS !== $imagine_hosts) {
    http_response_code(503);
    exit(78); // Configuration contradictoire : aucun élargissement silencieux.
}
unset($imagine_hosts);
if (!defined('DISALLOW_FILE_EDIT')) {
    define('DISALLOW_FILE_EDIT', true);
}

add_filter('pre_wp_mail', static fn (): bool => false, PHP_INT_MAX);

function imagineUpdateUrlAllowed(string $url): bool
{
    if (!defined('IMAGINE_STAGING_VERIFIED') || IMAGINE_STAGING_VERIFIED !== true
        || preg_match('/[\\\\\x00-\x20\x7f]/', $url)) {
        return false;
    }
    $parts = parse_url($url);
    if (!is_array($parts) || ($parts['scheme'] ?? '') !== 'https'
        || isset($parts['user']) || isset($parts['pass'])
        || (isset($parts['port']) && $parts['port'] !== 443)) {
        return false;
    }
    $host = strtolower($parts['host'] ?? '');
    return (bool) preg_match('/^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:wordpress\.org|woocommerce\.com)$/D', $host);
}

add_filter('pre_http_request', static function (mixed $pre, array $args, string $url): mixed {
    return imagineUpdateUrlAllowed($url) ? $pre
        : new \WP_Error('imagine_staging_offline', 'Sortie réseau interdite sur cette copie.');
}, PHP_INT_MAX, 3);
// Le transport Requests suit ses redirections sans repasser par pre_http_request.
// Refuser ce détour plutôt que laisser un hôte autorisé rediriger vers n'importe où.
add_filter('http_request_args', static function (array $args): array {
    $args['redirection'] = 0;
    return $args;
}, PHP_INT_MAX);
add_filter('block_local_requests', static fn (): bool => true, PHP_INT_MAX);
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
