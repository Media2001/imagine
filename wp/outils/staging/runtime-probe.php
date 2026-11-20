<?php

declare(strict_types=1);

namespace Imagine\Staging;

/** À appeler dans un bootstrap WordPress isolé APRÈS contrôle des données/fichiers, jamais au require du bridge. */
function runtimeProbe(): array
{
    if (!function_exists('wp_mail') || !function_exists('wp_remote_get')) {
        return [];
    }
    $mailFilter = apply_filters('pre_wp_mail', null, ['to' => ['sonde@example.org'], 'subject' => 'Sonde fictive', 'message' => 'Sonde fictive', 'headers' => [], 'attachments' => []]);
    $httpFilter = apply_filters('pre_http_request', false, [], 'https://probe.invalid');
    // Pas même un essai si le court-circuit n'est pas déjà installé.
    $mailBlocked = $mailFilter === false && wp_mail('sonde@example.org', 'Sonde fictive', 'Sonde fictive') === false;
    $httpBlocked = $httpFilter instanceof \WP_Error && is_wp_error(wp_remote_get('https://probe.invalid'));
    return [
        'mail_blocked' => $mailBlocked,
        'http_blocked' => $httpBlocked,
        'subscriptions_present' => class_exists('WCS_Staging'),
        'subscriptions_staging' => class_exists('WCS_Staging') ? \WCS_Staging::is_duplicate_site() === true : null,
        'environment_staging' => wp_get_environment_type() === 'staging' && defined('WP_ENVIRONMENT_TYPE') && WP_ENVIRONMENT_TYPE === 'staging',
        'cron_disabled' => defined('DISABLE_WP_CRON') && DISABLE_WP_CRON === true && wp_get_ready_cron_jobs() === [],
        'as_async_disabled' => apply_filters('action_scheduler_allow_async_request_runner', true) === false,
        'as_runner_disabled' => has_action('action_scheduler_run_queue') === false,
        'gateways_disabled' => !function_exists('WC') || WC()->payment_gateways()->get_available_payment_gateways() === [],
    ];
}
