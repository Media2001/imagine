<?php

declare(strict_types=1);

// Faux moteur de hooks, pas WordPress : tests unitaires du mu-plugin uniquement.
$hooks = [];
function wp_get_environment_type(): string
{
    return getenv('IMAGINE_SYNTHETIC_ENV') ?: 'staging';
}
function add_filter(string $hook, callable $call, int $priority = 10, int $args = 1): void
{
    global $hooks;
    $hooks[$hook][$priority][] = $call;
}
function add_action(string $hook, callable $call, int $priority = 10, int $args = 1): void
{
    add_filter($hook, $call, $priority, $args);
}
function remove_all_actions(string $hook): void
{
    global $hooks;
    unset($hooks[$hook]);
}
function apply_filters(string $hook, mixed $value, mixed ...$args): mixed
{
    global $hooks;
    $list = $hooks[$hook] ?? [];
    ksort($list);
    foreach ($list as $callbacks) {
        foreach ($callbacks as $callback) {
            $value = $callback($value, ...$args);
        }
    }
    return $value;
}
class WP_Error
{
    public function __construct(public string $code, public string $message)
    {
    }
}
if (getenv('IMAGINE_SYNTHETIC_VERIFIED') === 'yes') {
    define('IMAGINE_STAGING_VERIFIED', true);
}
require __DIR__ . '/../../outils/staging/mu-plugins/000-imagine-staging-safety.php';
$checks = [
    apply_filters('pre_wp_mail', null, []) === false,
    apply_filters('pre_http_request', false, [], 'https://outside.invalid') instanceof WP_Error,
    apply_filters('woocommerce_subscriptions_is_duplicate_site', false) === true,
    apply_filters('action_scheduler_allow_async_request_runner', true) === false,
    apply_filters('pre_schedule_event', null, [], false) === false,
    apply_filters('pre_get_ready_cron_jobs', null) === [],
    apply_filters('woocommerce_available_payment_gateways', ['stripe' => 'invented']) === [],
    defined('DISABLE_WP_CRON') && DISABLE_WP_CRON === true,
    defined('WP_ENVIRONMENT_TYPE') && WP_ENVIRONMENT_TYPE === 'staging',
    WP_HTTP_BLOCK_EXTERNAL === true,
    defined('WP_ACCESSIBLE_HOSTS') && WP_ACCESSIBLE_HOSTS === (defined('IMAGINE_STAGING_VERIFIED') ? '*.wordpress.org,*.woocommerce.com' : ''),
];
$verified = defined('IMAGINE_STAGING_VERIFIED');
foreach (['https://api.wordpress.org/core/version-check/1.7/', 'https://downloads.wordpress.org/plugin/synthetic.zip', 'https://updates.woocommerce.com/'] as $url) {
    $checks[] = (apply_filters('pre_http_request', false, [], $url) === false) === $verified;
}
foreach (['https://wordpress.org.evil.invalid/', 'https://api.wordpress.org.evil.invalid/',
    'https://evilwordpress.org/', 'https://outside.invalid/', 'https://127.0.0.1/',
    'https://api.wordpress.org:8443/', 'http://api.wordpress.org/',
    'https://user:password@api.wordpress.org/', 'https://api.wordpress.org./',
    'https://api.wordpress.org\\@outside.invalid/', 'ftp://api.wordpress.org/'] as $url) {
    $checks[] = apply_filters('pre_http_request', false, [], $url) instanceof WP_Error;
}
if (in_array(false, $checks, true)) {
    throw new RuntimeException('MU filtre manquant');
}
try {
    apply_filters('action_scheduler_before_execute', 1);
    throw new RuntimeException('AS exécuté');
} catch (LogicException) {
}
print('OK ' . (count($checks) + 1) . " assertions MU\n");
