<?php

declare(strict_types=1);

namespace Imagine\ExternalDoors;

final class Inventory
{
    public static function collect(string $site, string $asOf): array
    {
        $clock = \DateTimeImmutable::createFromFormat('!Y-m-d\TH:i:s\Z', $asOf, new \DateTimeZone('UTC'));
        if (!$clock || $clock->format('Y-m-d\TH:i:s\Z') !== $asOf) {
            throw new \RuntimeException('A21_CLOCK_INVALID');
        }
        // Native Action Scheduler pre-filters also cover a neutralised empty queue.
        // WordPress converts these preinitialised hooks before loading site plugins.
        foreach (['enqueue_async', 'schedule_single', 'schedule_recurring', 'schedule_cron'] as $kind) {
            $GLOBALS['wp_filter']['pre_as_' . $kind . '_action'][PHP_INT_MAX][] = [
                'function' => static function (): int {
                    \Imagine\PublicAddresses\Runtime::$guards['scheduled']++;
                    return 0;
                },
                'accepted_args' => 0,
            ];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        if (!function_exists('WC') || !class_exists('WC_Webhook')) {
            throw new \RuntimeException('A21_NATIVE_API_UNAVAILABLE');
        }
        $neutralised = get_option('imagine_staging_disabled_plugins', null) !== null;
        $keys = [];
        $hooks = [];
        $helper = [];
        if (!$neutralised) {
            global $wpdb;
            // Never read descriptions, keys, fragments, nonces, account IDs or webhook names/secrets.
            $keys = $wpdb->get_results(
                "SELECT permissions,last_access FROM `{$wpdb->prefix}woocommerce_api_keys`",
                ARRAY_A
            );
            if (!is_array($keys) || $wpdb->last_error !== '') {
                throw new \RuntimeException('A21_QUERY_FAILED');
            }
            $hooks = $wpdb->get_results("SELECT status,topic,delivery_url FROM `{$wpdb->prefix}wc_webhooks`", ARRAY_A);
            if (!is_array($hooks) || $wpdb->last_error !== '') {
                throw new \RuntimeException('A21_QUERY_FAILED');
            }
            $helper = get_option('woocommerce_helper_data', []);
            if (!is_array($helper)) {
                throw new \RuntimeException('A21_STORE_SCHEMA_UNSUPPORTED');
            }
        }
        $data = Analysis::report(
            $keys,
            $hooks,
            $helper,
            $neutralised,
            $clock,
            wp_timezone(),
            (string) get_option('home')
        );
        return ['schema' => 'imagine-a21-external-doors-v1', 'read_only' => true,
            'storage' => get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic',
            'as_of_utc' => $asOf] + $data + [
                'outbound_attempts' => \Imagine\PublicAddresses\Runtime::$guards,
                'basis' => [
                    'keys' => 'Droits déclarés ; accès local au fuseau WordPress ; '
                        . 'jamais et plus de douze mois disjoints.',
                    'destinations' => 'Nom d’hôte exact sans DNS ; casse et point final neutralisés ; '
                        . 'seuls les actifs.',
                    'topics' => 'Identifiants standard fermés ; '
                        . 'sujets libres et actions personnalisées regroupés sous unknown.',
                    'store' => 'Déclaration locale auth.access_token ; aucune vérification distante.',
                ],
            ];
    }
}
