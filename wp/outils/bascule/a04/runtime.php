<?php

declare(strict_types=1);

namespace Imagine\Bascule;

final class Runtime
{
    public static function need(bool $ok, string $code): void
    {
        if (!$ok) {
            throw new \RuntimeException($code);
        }
    }

    public static function run(): array
    {
        global $wpdb, $wp_db_version;
        $component = (string) getenv('IMAGINE_A04_COMPONENT');
        $mode = (string) getenv('IMAGINE_A04_MODE');
        self::need(in_array($mode, ['guard', 'migrate', 'verify'], true), 'A04_MODE');
        require_once dirname(__DIR__, 2) . '/staging/runtime-probe.php';
        $probe = \Imagine\Staging\runtimeProbe();
        foreach (['mail_blocked', 'http_blocked', 'subscriptions_staging', 'environment_staging',
            'cron_disabled', 'as_async_disabled', 'as_runner_disabled', 'gateways_disabled'] as $key) {
            self::need(($probe[$key] ?? null) === true, 'A04_RUNTIME_UNSAFE');
        }
        $migrations = [];
        if ($mode !== 'guard') {
            if ($component === 'core') {
                self::need((string) get_option('db_version') === (string) $wp_db_version, 'A04_CORE_DB');
                $migrations[] = 'wp core update-db; db_version=' . $wp_db_version;
            } elseif ($component === 'woocommerce') {
                self::need(version_compare((string) get_option('woocommerce_db_version'), WC()->version, '>='), 'A04_WC_DB');
                $migrations[] = 'wp wc update; woocommerce_db_version=' . get_option('woocommerce_db_version');
            } elseif ($component === 'woocommerce-subscriptions') {
                self::need(class_exists('WC_Subscriptions_Upgrader'), 'A04_SUBSCRIPTIONS_UPGRADER');
                if ($mode === 'migrate' && (string) get_option(\WC_Subscriptions::PLUGIN_VERSION_OPTION_NAME) !== \WC_Subscriptions::$version) {
                    \WC_Subscriptions_Upgrader::upgrade();
                    $migrations[] = 'WC_Subscriptions_Upgrader::upgrade';
                }
                self::need((string) get_option(\WC_Subscriptions::PLUGIN_VERSION_OPTION_NAME) === \WC_Subscriptions::$version, 'A04_SUBSCRIPTIONS_DB');
                self::need((string) get_option('woocommerce_subscriptions_active_version') === \WC_Subscriptions_Core_Plugin::instance()->get_library_version(), 'A04_SUBSCRIPTIONS_LIBRARY_DB');
            } elseif ($component === 'woocommerce-memberships') {
                $handler = wc_memberships()->get_lifecycle_handler();
                if ($mode === 'migrate') {
                    self::need(is_callable([$handler, 'init']), 'A04_MEMBERSHIPS_UPGRADER');
                    $handler->init();
                    $migrations[] = 'WC_Memberships lifecycle init';
                }
                self::need((string) get_option('wc_memberships_version') === wc_memberships()->get_version(), 'A04_MEMBERSHIPS_DB');
            }
            // Native Woo CLI drains its own callbacks synchronously. Other pending
            // migration work must never be mistaken for completion or run as a global queue.
            $rows = $wpdb->get_results("SELECT action_id,hook,status FROM {$wpdb->prefix}actionscheduler_actions
                WHERE status IN ('pending','in-progress','failed') ORDER BY action_id", ARRAY_A);
            self::need($wpdb->last_error === '', 'A04_SQL_READ');
            $prefix = match ($component) {
                'woocommerce' => '(?:woocommerce|wp_.*wc_updater|wc_updater)',
                'woocommerce-subscriptions' => '(?:wcs|woocommerce_subscriptions)',
                'woocommerce-memberships' => 'wc_memberships',
                default => '(?!)',
            };
            foreach ($rows as $row) {
                if (preg_match('/^' . $prefix . '.*(?:upgrade|migrate|migration|run_update_callback)/', $row['hook'])) {
                    throw new \RuntimeException('A04_PENDING_MIGRATION_ADAPTER_REQUIRED');
                }
            }
            $batches = $wpdb->get_col("SELECT option_name FROM {$wpdb->options} WHERE
                option_name LIKE '%\\_batch\\_%' OR option_name LIKE 'wcs%upgrade%'");
            self::need($wpdb->last_error === '', 'A04_SQL_READ');
            foreach ($batches as $name) {
                if (preg_match('/^' . $prefix . '.*_batch_/', $name)) {
                    self::need(empty(get_option($name)), 'A04_BACKGROUND_MIGRATION_ADAPTER_REQUIRED');
                }
            }
            foreach (_get_cron_array() ?: [] as $hooks) {
                foreach (array_keys($hooks) as $hook) {
                    self::need(!preg_match('/^' . $prefix . '.*(?:upgrade|migrate|migration)/', $hook), 'A04_CRON_MIGRATION_ADAPTER_REQUIRED');
                }
            }
        }
        self::need($wpdb->last_error === '', 'A04_SQL_READ');
        return ['safe' => true, 'complete' => true, 'component' => $component,
            'migrations' => $migrations];
    }
}

try {
    echo 'A04_JSON=' . json_encode(Runtime::run(), JSON_THROW_ON_ERROR) . "\n";
} catch (\Throwable $error) {
    $code = preg_match('/\AA04_[A-Z_]+\z/D', $error->getMessage())
        ? $error->getMessage() : 'A04_RUNTIME_FAILED';
    fwrite(STDERR, $code . "\n");
    exit(1);
}
