<?php

declare(strict_types=1);

// Hooks/API synthétiques ; aucune preuve WordPress réelle, aucun transport.
require __DIR__ . '/mu-plugin.php';
require __DIR__ . '/../../outils/staging/runtime-probe.php';
$mailCalls = 0;
$transports = 0;
function wp_mail(mixed ...$args): bool
{
    global $mailCalls, $transports;
    ++$mailCalls;
    $pre = apply_filters('pre_wp_mail', null, []);
    if ($pre !== null) { return $pre; }
    ++$transports;
    return true;
}
function wp_remote_get(string $url): mixed
{
    $pre = apply_filters('pre_http_request', false, [], $url);
    if ($pre === false) { throw new LogicException('TRANSPORT SYNTHETIQUE INTERDIT'); }
    return $pre;
}
function is_wp_error(mixed $value): bool { return $value instanceof WP_Error; }
function wp_get_ready_cron_jobs(): array { return apply_filters('pre_get_ready_cron_jobs', []); }
function has_action(string $hook): bool { global $hooks; return isset($hooks[$hook]); }
if (getenv('IMAGINE_SYNTHETIC_SUBSCRIPTIONS') === 'yes') {
    class WCS_Staging
    {
        public static function is_duplicate_site(): bool { return apply_filters('woocommerce_subscriptions_is_duplicate_site', false); }
    }
}
$proof = Imagine\Staging\runtimeProbe();
$present = getenv('IMAGINE_SYNTHETIC_SUBSCRIPTIONS') === 'yes';
$checks = [
    $proof['mail_blocked'] === true,
    $mailCalls === 1 && $transports === 0,
    $proof['subscriptions_present'] === $present,
    $proof['subscriptions_staging'] === ($present ? true : null),
    $proof['http_blocked'] === true,
    $proof['environment_staging'] === true,
    $proof['cron_disabled'] === true,
    $proof['as_async_disabled'] === true,
    $proof['as_runner_disabled'] === true,
    $proof['gateways_disabled'] === true, // Woo absent : pas de passerelle disponible.
];
remove_all_actions('pre_wp_mail');
$proof = Imagine\Staging\runtimeProbe();
$checks[] = $proof['mail_blocked'] === false;
$checks[] = $mailCalls === 1 && $transports === 0; // Jamais d'essai si le filtre manque.
if (in_array(false, $checks, true)) {
    throw new RuntimeException('Contrat sonde runtime incomplet');
}
print('OK '.count($checks)." assertions runtime contract\n");
