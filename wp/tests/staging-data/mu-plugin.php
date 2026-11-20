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
];
if (in_array(false, $checks, true)) {
    throw new RuntimeException('MU filtre manquant');
}
try {
    apply_filters('action_scheduler_before_execute', 1);
    throw new RuntimeException('AS exécuté');
} catch (LogicException) {
}
print('OK ' . (count($checks) + 1) . " assertions MU\n");
