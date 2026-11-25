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

    public static function trace(array $event): void
    {
        $path = (string) getenv('IMAGINE_A04_JOURNAL');
        if ($path === '') {
            return;
        }
        self::need(!is_link($path), 'A04_JOURNAL');
        $handle = fopen($path, 'ab');
        self::need(is_resource($handle), 'A04_JOURNAL');
        try {
            self::need(flock($handle, LOCK_EX), 'A04_JOURNAL');
            $line = json_encode(['utc' => gmdate('c')] + $event, JSON_THROW_ON_ERROR) . "\n";
            self::need(fwrite($handle, $line) === strlen($line) && fflush($handle) && fsync($handle), 'A04_JOURNAL');
        } finally {
            fclose($handle);
        }
    }

    public static function wooMigrations(): array
    {
        $allowed = [];
        foreach (\WC_Install::get_db_update_callbacks() as $callbacks) {
            $allowed = array_merge($allowed, $callbacks);
        }
        // This native Woo migration deliberately uses the shared callback hook
        // but is registered outside WC_Install::$db_updates (Woo 11.1.1).
        $allowed[] = ['Automattic\\WooCommerce\\Internal\\VariationGallery\\Migration', 'run'];
        $executed = [];
        $start = microtime(true);
        for ($batch = 0; $batch < 10000; $batch++) {
            $ids = as_get_scheduled_actions(['hook' => 'woocommerce_run_update_callback',
                'group' => 'woocommerce-db-updates', 'status' => 'pending',
                'per_page' => 1, 'orderby' => 'action_id', 'order' => 'ASC'], 'ids');
            if (!$ids) {
                return array_merge($executed, self::wooFinalize());
            }
            self::need(microtime(true) - $start < 120, 'A04_MIGRATION_LIMIT');
            $id = (int) reset($ids);
            $store = \ActionScheduler::store();
            $action = $store->fetch_action($id);
            $args = $action->get_args();
            $callback = $args['update_callback'] ?? null;
            $function = is_string($callback) && preg_match('/\Awc_update_[0-9][A-Za-z0-9_]*\z/D', $callback) === 1;
            $method = is_array($callback) && array_is_list($callback) && count($callback) === 2
                && is_string($callback[0]) && str_starts_with($callback[0], 'Automattic\\WooCommerce\\')
                && is_string($callback[1]) && preg_match('/\A[A-Za-z][A-Za-z0-9_]*\z/D', $callback[1]) === 1;
            self::need(count($args) === 1 && ($function || $method)
                && in_array($callback, $allowed, true), 'A04_CALLBACK_REFUSED');
            // Only this native callback and this exact action. The staging AS
            // blocker stays installed; no global queue or payment hook is run.
            $label = is_array($callback) ? implode('::', $callback) : $callback;
            self::trace(['component' => 'woocommerce', 'action_id' => $id, 'callback' => $label, 'stage' => 'begin']);
            \WC_Install::run_update_callback($callback);
            $store->mark_complete($id);
            self::need($store->get_status($id) === 'complete', 'A04_ACTION_READBACK');
            self::trace(['component' => 'woocommerce', 'action_id' => $id, 'callback' => $label, 'stage' => 'complete']);
            $executed[] = $label;
        }
        throw new \RuntimeException('A04_MIGRATION_LIMIT');
    }

    public static function wooFinalize(): array
    {
        $ids = as_get_scheduled_actions(['hook' => 'woocommerce_update_db_to_current_version',
            'group' => 'woocommerce-db-updates', 'status' => 'pending', 'per_page' => 100], 'ids');
        $updates = \WC_Install::get_db_update_callbacks();
        $expected = array_key_last($updates);
        $expected = version_compare(WC()->version, $expected, '>') ? WC()->version : $expected;
        foreach ($ids as $id) {
            $store = \ActionScheduler::store();
            $args = $store->fetch_action((int) $id)->get_args();
            self::need($args === ['version' => $expected], 'A04_DB_VERSION_ACTION_REFUSED');
            \WC_Install::update_db_version($expected);
            $store->mark_complete((int) $id);
            self::need($store->get_status((int) $id) === 'complete', 'A04_ACTION_READBACK');
        }
        return $ids ? ['WC_Install::update_db_version=' . $expected] : [];
    }

    public static function run(): array
    {
        global $wpdb, $wp_db_version;
        $component = (string) getenv('IMAGINE_A04_COMPONENT');
        $mode = (string) getenv('IMAGINE_A04_MODE');
        self::need(in_array($mode, ['guard', 'migrate', 'verify'], true), 'A04_MODE');
        require_once dirname(__DIR__, 2) . '/staging/runtime-probe.php';
        $probe = \Imagine\Staging\runtimeProbe();
        $expectedEnvironment = (string) getenv('IMAGINE_A04_EXPECTED_ENV');
        self::need(in_array($expectedEnvironment, ['staging', 'production'], true)
            && wp_get_environment_type() === $expectedEnvironment, 'A04_ENVIRONMENT');
        foreach (['mail_blocked', 'http_blocked', 'subscriptions_staging',
            'cron_disabled', 'as_async_disabled', 'as_runner_disabled', 'gateways_disabled'] as $key) {
            self::need(($probe[$key] ?? null) === true, 'A04_RUNTIME_UNSAFE');
        }
        self::trace(['component' => $component, 'mode' => $mode, 'stage' => 'runtime_safe', 'environment' => $expectedEnvironment]);
        $migrations = [];
        if ($mode !== 'guard') {
            if ($component === 'core') {
                self::need((string) get_option('db_version') === (string) $wp_db_version, 'A04_CORE_DB');
                $migrations[] = 'wp core update-db; db_version=' . $wp_db_version;
            } elseif ($component === 'woocommerce') {
                if ($mode === 'migrate') {
                    $migrations = self::wooMigrations();
                }
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
                require_once WC_ABSPATH . 'includes/admin/wc-admin-functions.php';
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
                if ($name === 'wcs_pending_batch_processes') {
                    // The native notifications processor is recurring operational
                    // work, not a schema/data upgrader. Preserve it; never send it.
                    $processors = get_option($name, []);
                    self::need(is_array($processors)
                        && array_diff($processors, ['WCS_Notifications_Batch_Processor']) === [],
                        'A04_BACKGROUND_MIGRATION_ADAPTER_REQUIRED');
                    continue;
                }
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
    Runtime::trace(['component' => (string) getenv('IMAGINE_A04_COMPONENT'),
        'stage' => 'error', 'class' => get_class($error), 'line' => $error->getLine(),
        'file' => basename($error->getFile())]);
    $code = preg_match('/\AA04_[A-Z_]+\z/D', $error->getMessage())
        ? $error->getMessage() : 'A04_RUNTIME_FAILED';
    fwrite(STDERR, $code . "\n");
    exit(1);
}
