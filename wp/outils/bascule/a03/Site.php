<?php

declare(strict_types=1);

namespace Imagine\NonRegression;

use Automattic\WooCommerce\Utilities\OrderUtil;

final class Site
{
    private static bool $verified = false;
    private static bool $safeRuntime = false;

    public static function identifier(string $value): string
    {
        return \Imagine\Audit\Audit::identifier($value);
    }

    public static function json(string $path): array
    {
        if (!is_file($path) || is_link($path) || filesize($path) > 16777216) {
            throw new \RuntimeException('A03_JSON_FILE');
        }
        $value = json_decode(file_get_contents($path), true, 64, JSON_THROW_ON_ERROR);
        if (!is_array($value)) {
            throw new \RuntimeException('A03_JSON_FILE');
        }
        return $value;
    }

    public static function bootstrap(string $site, bool $write): void
    {
        self::$verified = Policy::verified(self::json($site . '/.imagine-staging-verified.json'));
        if (!self::$verified) {
            throw new \RuntimeException('A03_NOT_VERIFIED');
        }
        $guard = $site . '/wp-content/mu-plugins/000-imagine-staging-safety.php';
        if (
            !is_file($guard) || is_link($guard) || hash_file('sha256', $guard) !== hash_file(
                'sha256',
                dirname(__DIR__, 2) . '/staging/mu-plugins/000-imagine-staging-safety.php'
            )
        ) {
            throw new \RuntimeException('A03_SAFETY_BYTES');
        }
        foreach (['db.php', 'object-cache.php', 'advanced-cache.php'] as $dropin) {
            $file = $site . '/wp-content/' . $dropin;
            if (file_exists($file) || is_link($file)) {
                throw new \RuntimeException('A03_DB_OR_CACHE_DROPIN');
            }
        }
        define('IMAGINE_AUDIT_LIBRARY_ONLY', true);
        require_once dirname(__DIR__) . '/audit';
        $config = \Imagine\Audit\Audit::config(file_get_contents($site . '/wp-config.php'));
        $db = new \PDO(Policy::dsn($config), $config['DB_USER'], $config['DB_PASSWORD'], [\PDO::ATTR_ERRMODE
            => \PDO::ERRMODE_EXCEPTION]);
        if (!$write) {
            foreach ($db->query('SHOW GRANTS')->fetchAll(\PDO::FETCH_COLUMN) as $grant) {
                if (
                    !preg_match('/\AGRANT (?:USAGE|SELECT) ON /D', $grant) || str_contains(
                        $grant,
                        'WITH GRANT OPTION'
                    )
                ) {
                    throw new \RuntimeException('A03_SELECT_ACCOUNT_REQUIRED');
                }
            }
        }
        if ($write) {
            foreach (
                $db->query('SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND' .
                ' TABLE_TYPE=\'BASE TABLE\'')->fetchAll(\PDO::FETCH_COLUMN) as $engine
            ) {
                if ($engine !== 'InnoDB') {
                    throw new \RuntimeException('A03_TRANSACTIONAL_TABLES_REQUIRED');
                }
            }
        }
            // WordPress officially preserves an already supplied $wpdb in require_wp_db().
            // Read failures must throw immediately, before an API can clear last_error.
            // Keep all native renewal writes rollback-only, including nested WC transactions.
            define('ABSPATH', $site . '/');
            define('WP_DEBUG', false);
            define('WP_DEBUG_DISPLAY', false);
            require_once ABSPATH . 'wp-includes/plugin.php';
            require_once ABSPATH . 'wp-includes/class-wpdb.php';
            $GLOBALS['wpdb'] = new class (
                $config['DB_USER'],
                $config['DB_PASSWORD'],
                $config['DB_NAME'],
                $config['DB_HOST']
) extends \wpdb {
                private bool $closed = false;
                private bool $probe = false;

                public function beginProbe(): void
                {
                    if (parent::query('START TRANSACTION') === false) {
                        throw new \RuntimeException('A03_TRANSACTION_FAILED');
                    }
                    $this->probe = true;
                }

                public function finishProbe(): void
                {
                    parent::query('ROLLBACK');
                    $this->closed = true;
                }

                public function query($query)
                {
                    if ($this->probe && preg_match('/\A\s*(?:START|BEGIN|COMMIT|ROLLBACK|SAVEPOINT|RELEASE)\b/i', $query)) {
                        return 0;
                    }
                    if (
                        $this->probe && preg_match(
                            '/\A\s*(?:CREATE|ALTER|DROP|TRUNCATE|RENAME|GRANT|REVOKE|LOCK|UNLOCK)\b/i',
                            $query
                        )
                    ) {
                        throw new \RuntimeException('A03_DDL_DURING_PROBE');
                    }
                    if ($this->closed && !preg_match('/\A\s*(?:SELECT|SHOW|DESCRIBE)\b/i', $query)) {
                        return false;
                    }
                    $result = parent::query($query);
                    if ($result === false && preg_match('/\A\s*(?:SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $query)) {
                        throw new \RuntimeException('A03_SQL_READ');
                    }
                    return $result;
                }
            };
            $GLOBALS['wpdb']->suppress_errors(true);
        if ($write) {
            $GLOBALS['wpdb']->beginProbe();
        }
        $db = null;
        unset($config);
        // No raw bootstrap output, personal values or plugin messages leave this process.
        require $site . '/wp-load.php';
        global $wpdb;
        $wpdb->suppress_errors(true);
        if (!function_exists('wc_memberships_user_can') || !function_exists('wcs_get_subscriptions')) {
            throw new \RuntimeException('A03_REQUIRED_EXTENSIONS');
        }
        require_once dirname(__DIR__, 2) . '/staging/runtime-probe.php';
        $probe = \Imagine\Staging\runtimeProbe();
        $required = ['mail_blocked', 'http_blocked', 'subscriptions_staging', 'environment_staging',
            'cron_disabled', 'as_async_disabled', 'as_runner_disabled', 'gateways_disabled'];
        foreach ($required as $key) {
            if (($probe[$key] ?? null) !== true) {
                throw new \RuntimeException('A03_RUNTIME_UNSAFE');
            }
        }
        self::$safeRuntime = true;
        if (!$write) {
            if (
                $wpdb->query('SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ') === false
                || $wpdb->query('START TRANSACTION READ ONLY') === false
            ) {
                throw new \RuntimeException('A03_TRANSACTION_FAILED');
            }
        }
    }

    private static function read(callable $read): mixed
    {
        global $wpdb;
        $wpdb->last_error = '';
        $value = $read();
        if ($wpdb->last_error !== '' && preg_match('/\A\s*(?:SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $wpdb->last_query)) {
            throw new \RuntimeException('A03_SQL_READ');
        }
        return $value;
    }

    private static function subscriptions(): array
    {
        $result = [];
        for ($page = 1;; $page++) {
            $batch = self::read(static fn(): array => wcs_get_subscriptions([
                'subscriptions_per_page' => 100, 'paged' => $page,
                'subscription_status' => 'any', 'orderby' => 'ID', 'order' => 'ASC']));
            foreach ($batch as $s) {
                $result[$s->get_id()] = $s;
            }
            if (count($batch) < 100) {
                break;
            }
            if ($page > 10000) {
                throw new \RuntimeException('A03_SUBSCRIPTIONS_LIMIT');
            }
        }
        ksort($result, SORT_NUMERIC);
        return $result;
    }

    public static function collect(array $settings): array
    {
        global $wpdb;
        $subs = self::subscriptions();
        $rows = [];
        $counts = ['status' => [], 'gateway' => [], 'period' => []];
        $userSubs = [];
        foreach ($subs as $id => $s) {
            $row = ['status' => self::identifier($s->get_status()), 'gateway'
                => self::identifier($s->get_payment_method() ?: 'manual'),
                'period' => self::identifier($s->get_billing_period()), 'interval' => (int) $s->get_billing_interval(),
                'next_payment_utc' => $s->get_date('next_payment', 'gmt')];
            $rows[$id] = $row;
            $userSubs[$s->get_user_id()][] = $row['status'];
            foreach (
                ['status' => $row['status'], 'gateway' => $row['gateway'], 'period' => $row['interval']
                . '-' . $row['period']] as $kind => $key
            ) {
                $counts[$kind][$key] = ($counts[$kind][$key] ?? 0) + 1;
            }
        }
        foreach ($counts as &$group) {
            ksort($group);
        }
        unset($group);
        $userMembers = [];
        $memberships = [];
        $membershipQuery = "SELECT ID FROM {$wpdb->posts} WHERE post_type='wc_user_membership' ORDER BY ID";
        foreach (self::read(static fn() => $wpdb->get_col($membershipQuery)) as $id) {
            $m = self::read(static fn() => wc_memberships_get_user_membership((int) $id));
            if (!$m) {
                throw new \RuntimeException('A03_MEMBERSHIP_READ');
            }
            $state = self::identifier($m->get_status());
            $userMembers[$m->get_user_id()][] = $state;
            $memberships[(int) $id] = ['user_id' => $m->get_user_id(), 'plan_id' => $m->get_plan_id(),
                'status' => $state];
        }
        $samples = [];
        $membershipStates = ['none'];
        $subscriptionStates = ['none'];
        foreach (self::read(static fn() => $wpdb->get_col("SELECT ID FROM {$wpdb->users} ORDER BY ID")) as $id) {
            $id = (int) $id;
            if (
                self::read(static fn(): bool => user_can($id, 'manage_options')
                || user_can($id, 'manage_woocommerce') || is_super_admin($id))
            ) {
                continue;
            }
            $ms = array_unique($userMembers[$id] ?? ['none']);
            $ss = array_unique($userSubs[$id] ?? ['none']);
            sort($ms);
            sort($ss);
            $key = implode('+', $ms) . ':' . implode('+', $ss);
            $samples[$key] ??= $id;
            $membershipStates = array_merge($membershipStates, $ms);
            $subscriptionStates = array_merge($subscriptionStates, $ss);
        }
        ksort($samples);
        $access = [];
        $targets = $settings['restricted_ids'] ?? [];
        if (!$targets || !array_is_list($targets) || count($targets) > 100 || count($samples) > 1000) {
            throw new \RuntimeException('A03_SAMPLE_CONFIG');
        }
        foreach ($targets as $post) {
            if (!is_int($post) || !self::read(static fn(): bool => wc_memberships_is_post_content_restricted($post))) {
                throw new \RuntimeException('A03_CONTENT_NOT_RESTRICTED');
            }
            foreach (array_unique(array_merge([0], array_values($samples))) as $uid) {
                $access[$uid . ':' . $post] = self::read(
                    static fn(): bool => wc_memberships_user_can($uid, 'view', ['post' => $post])
                );
            }
        }
        ksort($access, SORT_NATURAL);
        $actions = [];
        $actionDays = [];
        foreach (
            self::read(static fn() => $wpdb->get_results("SELECT action_id,hook,scheduled_date_gmt FROM" .
            " {$wpdb->prefix}actionscheduler_actions WHERE status='pending' ORDER BY action_id", ARRAY_A)) as $a
        ) {
            $hook = self::identifier($a['hook']);
            $date = $a['scheduled_date_gmt'];
            if (!preg_match('/\A[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\z/D', $date)) {
                throw new \RuntimeException('A03_ACTION_DATE');
            }
            $actions[(int) $a['action_id']] = ['hook' => $hook, 'date' => $date];
            $key = $hook . ':' . substr($date, 0, 10);
            $actionDays[$key] = ($actionDays[$key] ?? 0) + 1;
        }
        ksort($actionDays);
        [$months, $orders] = self::orders($settings['as_of_month'] ?? '');
        $membershipStates = array_values(array_unique($membershipStates));
        $subscriptionStates = array_values(array_unique($subscriptionStates));
        sort($membershipStates);
        sort($subscriptionStates);
        return ['schema' => 'imagine-a03-v1', 'generated_at_utc' => gmdate('c'),
            'versions' => ['wordpress' => get_bloginfo('version'), 'php' => PHP_VERSION, 'woocommerce'
                => WC()->version, 'memberships' => wc_memberships()->get_version(), 'subscriptions'
                => \WC_Subscriptions::$version],
            'storage' => OrderUtil::custom_orders_table_usage_is_enabled() ? 'hpos' : 'classic',
            'sample_states' => ['membership' => array_fill_keys($membershipStates, true),
                'subscription' => array_fill_keys($subscriptionStates, true)],
                'samples' => $samples,
            'memberships' => $memberships, 'access' => $access, 'subscriptions' => $rows,
                'subscription_counts' => $counts,
            'actions' => $actions, 'action_days' => $actionDays, 'order_months' => $months, 'orders' => $orders,
            'pages' => self::pages($settings['pages'] ?? []), 'renewal' => ['enabled' => false]];
    }

    private static function orders(string $month): array
    {
        if (!preg_match('/\A[0-9]{4}-(?:0[1-9]|1[0-2])\z/D', $month)) {
            throw new \RuntimeException('A03_MONTH_CONFIG');
        }
        $end = new \DateTimeImmutable($month . '-01 00:00:00', new \DateTimeZone('UTC'));
        $start = $end->modify('-11 months');
        $months = [];
        for ($i = 0; $i < 12; $i++) {
            $months[] = $start->modify('+' . $i . ' months')->format('Y-m');
        }
        $result = [];
        for ($page = 1;; $page++) {
            $orders = self::read(static fn(): array => wc_get_orders([
                'type' => 'shop_order', 'status' => array_keys(wc_get_order_statuses()),
                'limit' => 100, 'page' => $page, 'orderby' => 'ID', 'order' => 'ASC']));
            foreach ($orders as $order) {
                $date = $order->get_date_created();
                if (!$date) {
                    throw new \RuntimeException('A03_ORDER_DATE');
                }
                $m = gmdate('Y-m', $date->getTimestamp());
                if (!in_array($m, $months, true)) {
                    continue;
                }
                $currency = $order->get_currency();
                if (!preg_match('/\A[A-Z]{3}\z/D', $currency)) {
                    throw new \RuntimeException('A03_ORDER_CURRENCY');
                }
                $key = $m . ':' . self::identifier($order->get_status()) . ':' . $currency;
                $precision = wc_get_price_decimals();
                $result[$key] ??= ['count' => 0, 'amount_minor' => 0, 'decimals' => $precision];
                $value = $order->get_total();
                if (!preg_match('/\A-?[0-9]{1,10}(?:\.[0-9]{1,8})?\z/D', $value)) {
                    throw new \RuntimeException('A03_ORDER_AMOUNT');
                }
                $result[$key]['count']++;
                $result[$key]['amount_minor'] += (int) round((float) $value * (10 ** $precision));
            }
            if (count($orders) < 100) {
                break;
            }
            if ($page > 10000) {
                throw new \RuntimeException('A03_ORDERS_LIMIT');
            }
        }
        ksort($result);
        return [$months, $result];
    }

    private static function pages(array $pages): array
    {
        if (array_keys($pages) !== ['home', 'open', 'restricted', 'shop', 'cart', 'checkout', 'account']) {
            throw new \RuntimeException('A03_PAGES_CONFIG');
        }
        $base = rtrim(home_url(), '/');
        $result = [];
        foreach ($pages as $key => $page) {
            $path = $page['path'] ?? '';
            $marker = $page['marker'] ?? '';
            if (
                !is_string($path) || !preg_match('~\A/(?!/)[A-Za-z0-9_/?=&.%-]*\z~D', $path)
                || !is_string($marker) || !preg_match('/\A[A-Za-z0-9_-]{3,100}\z/D', $marker)
            ) {
                throw new \RuntimeException('A03_PAGE_PATH_OR_MARKER');
            }
            $url = $base . $path;
            $first = null;
            $status = 0;
            $body = '';
            for ($redirect = 0; $redirect < 4; $redirect++) {
                $context = stream_context_create(['http' => ['method' => 'GET', 'follow_location' => 0,
                    'ignore_errors' => true, 'timeout' => 15, 'header' => "Connection: close\r\n"]]);
                $http_response_header = [];
                $handle = @fopen($url, 'rb', false, $context);
                $body = $handle === false ? '' : stream_get_contents($handle, 4194305);
                if (is_resource($handle)) {
                    fclose($handle);
                }
                $location = null;
                foreach ($http_response_header as $header) {
                    if (preg_match('~\AHTTP/\S+ ([0-9]{3})~', $header, $match)) {
                        $status = (int) $match[1];
                    }
                    if (stripos($header, 'Location: ') === 0) {
                        $location = trim(substr($header, 10));
                    }
                }
                $first ??= $status;
                if ($status < 300 || $status > 399 || $location === null) {
                    break;
                }
                $next = str_starts_with($location, '/') && !str_starts_with($location, '//') ? $base
                    . $location : $location;
                if (!str_starts_with($next, $base . '/') || preg_match('/[\\\\\x00-\x20]/', $next)) {
                    break;
                }
                $url = $next;
            }
            $result[$key] = ['status' => $first, 'final_status' => $status, 'marker'
                => strlen($body) <= 4194304 && str_contains($body, $marker),
                'php_error' => (bool) preg_match(
                    '/(?:Fatal error|Parse error|Warning:|Notice:|Deprecated:|Uncaught (?:Error|Exception))/i',
                    $body
                )];
        }
        return $result;
    }

    public static function renewal(): array
    {
        global $wpdb;
        if (!Policy::renewalAllowed(true, self::$verified, self::$safeRuntime)) {
            throw new \RuntimeException('A03_RENEWAL_UNSAFE');
        }
        $token = bin2hex(random_bytes(12));
        $uid = null;
        $subscription = null;
        $renewal = null;
        $subscriptionId = 0;
        $renewalId = 0;
        $actionIds = [];
        $result = ['enabled' => true, 'manual_only' => false, 'created' => false, 'linked' => false, 'pending'
            => false, 'cleaned' => false];
        try {
            $uid = wp_insert_user(['user_login' => 'imagine_a03_' . $token, 'user_email' => 'imagine-a03-'
                . $token . '@example.org', 'user_pass' => wp_generate_password(48), 'display_name'
                => 'Compte fictif A03']);
            if (is_wp_error($uid)) {
                throw new \RuntimeException('A03_TEST_USER');
            }
            update_user_meta($uid, 'imagine_a03_owned', $token);
            $subscription = wcs_create_subscription(['customer_id' => $uid, 'status' => 'pending',
                'billing_period' => 'month', 'billing_interval' => 1]);
            if (is_wp_error($subscription)) {
                throw new \RuntimeException('A03_TEST_SUBSCRIPTION');
            }
            $subscriptionId = $subscription->get_id();
            $subscription->update_meta_data('_imagine_a03_owned', $token);
            $subscription->set_payment_method('');
            $subscription->set_requires_manual_renewal(true);
            $fee = new \WC_Order_Item_Fee();
            $fee->set_name('Test fictif A03');
            $fee->set_amount('1.00');
            $fee->set_total('1.00');
            $subscription->add_item($fee);
            $subscription->calculate_totals(false);
            $subscription->save();
            $subscription->update_status('active');
            $result['manual_only'] = $subscription->get_requires_manual_renewal() === true
                && $subscription->get_payment_method() === '';
            if (!$result['manual_only']) {
                throw new \RuntimeException('A03_MANUAL_ONLY_REQUIRED');
            }
            $renewal = wcs_create_renewal_order($subscription);
            if (is_wp_error($renewal) || !$renewal instanceof \WC_Order) {
                throw new \RuntimeException('A03_RENEWAL_NOT_CREATED');
            }
            $renewalId = $renewal->get_id();
            $renewal->update_meta_data('_imagine_a03_owned', $token);
            $renewal->save();
            $result['created'] = $renewalId > 0 && $renewal->get_total() === '1.00';
            $result['linked'] = isset(wcs_get_subscriptions_for_renewal_order($renewal)[$subscriptionId]);
            $result['pending'] = $renewal->has_status('pending') && $renewal->get_date_paid() === null
                && $renewal->get_payment_method() === '';
            if (!$result['created'] || !$result['linked'] || !$result['pending']) {
                throw new \RuntimeException('A03_RENEWAL_ASSERTION');
            }
        } finally {
            // Capture only actions referring to the subscription owned by this invocation.
            if ($subscriptionId) {
                $query = "SELECT action_id,args FROM {$wpdb->prefix}actionscheduler_actions";
                foreach (self::read(static fn() => $wpdb->get_results($query, ARRAY_A)) as $row) {
                    $args = json_decode($row['args'], true);
                    if (is_array($args) && (int) ($args['subscription_id'] ?? 0) === $subscriptionId) {
                        $actionIds[] = (int) $row['action_id'];
                    }
                }
            }
            foreach ([$renewal, $subscription] as $object) {
                if ($object instanceof \WC_Abstract_Order) {
                    if ($object->get_meta('_imagine_a03_owned') !== $token) {
                        throw new \RuntimeException('A03_CLEANUP_OWNERSHIP');
                    }
                    $object->delete(true);
                }
            }
            foreach ($actionIds as $actionId) {
                if (\ActionScheduler::store()->fetch_action($actionId) instanceof \ActionScheduler_Action) {
                    try {
                        \ActionScheduler::store()->delete_action($actionId);
                    } catch (\InvalidArgumentException) {
                        // WCS deletion may already have removed precisely this action.
                    }
                }
                $wpdb->delete($wpdb->prefix . 'actionscheduler_logs', ['action_id' => $actionId], ['%d']);
            }
            if (is_int($uid)) {
                if (get_user_meta($uid, 'imagine_a03_owned', true) !== $token) {
                    throw new \RuntimeException('A03_CLEANUP_OWNERSHIP');
                }
                require_once ABSPATH . 'wp-admin/includes/user.php';
                wp_delete_user($uid);
            }
            $hpos = OrderUtil::custom_orders_table_usage_is_enabled();
            $table = $hpos ? $wpdb->prefix . 'wc_orders' : $wpdb->posts;
            $column = $hpos ? 'id' : 'ID';
            $remaining = (int) self::read(static fn() => $wpdb->get_var($wpdb->prepare(
                "SELECT COUNT(*) FROM $table WHERE $column IN (%d,%d)",
                $subscriptionId,
                $renewalId
            )));
            $result['cleaned'] = $remaining === 0
                && !self::read(static fn() => $wpdb->get_var($wpdb->prepare(
                    "SELECT ID FROM {$wpdb->users} WHERE ID=%d",
                    (int) $uid
                )));
            if (!$result['cleaned']) {
                throw new \RuntimeException('A03_CLEANUP_FAILED');
            }
        }
        return $result;
    }

    public static function main(array $args): int
    {
        $options = [];
        $write = false;
        foreach (array_slice($args, 1) as $arg) {
            if ($arg === '--renewal-test' && !$write) {
                $write = true;
                continue;
            }
            if (!preg_match('/\A--(wp-path|config|output)=(.+)\z/D', $arg, $m) || isset($options[$m[1]])) {
                throw new \RuntimeException('A03_USAGE');
            }
            $options[$m[1]] = $m[2];
        }
        if (count($options) !== 3 || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A03_USAGE');
        }
        $site = realpath($options['wp-path']);
        $parent = realpath(dirname($options['output']));
        $base = basename($options['output']);
        if (
            !$site || !$parent || !is_dir($site) || !preg_match('/\A[A-Za-z0-9_-]+\z/D', $base)
            || $parent === $site || str_starts_with($parent . '/', $site . '/') || file_exists($parent . '/' . $base)
        ) {
            throw new \RuntimeException('A03_PATH_UNSAFE_OR_EXISTS');
        }
        $settings = self::json($options['config']);
        self::bootstrap($site, $write);
        global $wpdb;
        if ($write) {
            try {
                $report = ['schema' => 'imagine-a03-v1', 'mode' => 'renewal_probe', 'renewal' => self::renewal()];
            } finally {
                $wpdb->finishProbe();
            }
        } else {
            $report = self::collect($settings);
            $wpdb->query('ROLLBACK');
        }
        self::writeReport($parent . '/' . $base, $report);
        return 0;
    }

    public static function writeReport(string $output, array $report): void
    {
        $json = json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR) . "\n";
        if (!@mkdir($output, 0700)) {
            throw new \RuntimeException('A03_OUTPUT_FAILED');
        }
        $file = $output . '/non-regression.json';
        if (@file_put_contents($file, $json) !== strlen($json) || !@chmod($file, 0600)) {
            if (is_file($file)) {
                @unlink($file);
            }
            throw new \RuntimeException('A03_OUTPUT_FAILED');
        }
    }
}
