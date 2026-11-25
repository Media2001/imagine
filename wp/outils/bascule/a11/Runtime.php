<?php

declare(strict_types=1);

namespace Imagine\PublicAddresses;

final class Runtime
{
    public static array $guards = ['http' => 0, 'mail' => 0, 'scheduled' => 0];

    public static function boot(string $site): void
    {
        $file = $site . '/wp-config.php';
        if (is_link($file) || realpath($file) !== $file || filesize($file) > 1048576) {
            throw new \RuntimeException('A11_CONFIG_UNSAFE');
        }
        $source = file_get_contents($file);
        $config = \Imagine\Audit\Audit::config($source);
        if (preg_match('/[\'\"](?:MULTISITE|SUBDOMAIN_INSTALL|WP_HOME|WP_SITEURL|WP_CONTENT_DIR|WP_PLUGIN_DIR|CUSTOM_USER_TABLE|CUSTOM_USER_META_TABLE)[\'\"]\s*,/', $source)) {
            throw new \RuntimeException('A11_CONFIG_OVERRIDE_UNSUPPORTED');
        }
        foreach (['db.php', 'object-cache.php', 'advanced-cache.php', 'sunrise.php'] as $dropin) {
            if (file_exists($site . '/wp-content/' . $dropin) || is_link($site . '/wp-content/' . $dropin)) {
                throw new \RuntimeException('A11_DROPIN_UNSUPPORTED');
            }
        }
        foreach (new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($site, \FilesystemIterator::SKIP_DOTS), \RecursiveIteratorIterator::SELF_FIRST) as $path) {
            if ($path->isLink()) {
                throw new \RuntimeException('A11_SYMLINK_UNSUPPORTED');
            }
        }
        define('ABSPATH', $site . '/');
        foreach ($config as $key => $value) {
            if ($key !== 'table_prefix') {
                define($key, $value);
            }
        }
        define('DB_CHARSET', 'utf8mb4');
        define('DB_COLLATE', '');
        define('WP_CACHE', false);
        define('WP_DEBUG', false);
        define('DISABLE_WP_CRON', true);
        define('AUTOMATIC_UPDATER_DISABLED', true);
        define('WP_AUTO_UPDATE_CORE', false);
        define('DISALLOW_FILE_MODS', true);
        define('WP_HTTP_BLOCK_EXTERNAL', true);
        define('WP_USE_THEMES', false);
        define('WP_ENVIRONMENT_TYPE', 'staging');
        $_SERVER['SERVER_PROTOCOL'] = 'HTTP/1.1';
        $_SERVER['REQUEST_METHOD'] = 'GET';
        require_once ABSPATH . 'wp-includes/plugin.php';
        require_once ABSPATH . 'wp-includes/class-wpdb.php';
        require_once __DIR__ . '/ReadOnlyDb.php';
        $GLOBALS['table_prefix'] = $config['table_prefix'];
        $GLOBALS['wpdb'] = new ReadOnlyDb($config['DB_USER'], $config['DB_PASSWORD'], $config['DB_NAME'], $config['DB_HOST']);
        $prefix = $config['table_prefix'];
        $home = $GLOBALS['wpdb']->get_var("SELECT option_value FROM `{$prefix}options` WHERE option_name='home' LIMIT 1");
        $origin = is_string($home) ? parse_url($home) : false;
        if (!$origin || !in_array($origin['scheme'] ?? '', ['http', 'https'], true) || empty($origin['host']) || isset($origin['user'])) {
            throw new \RuntimeException('A11_HOME_INVALID');
        }
        $_SERVER['HTTP_HOST'] = $origin['host'] . (isset($origin['port']) ? ':' . $origin['port'] : '');
        $_SERVER['SERVER_NAME'] = $origin['host'];
        $_SERVER['HTTPS'] = $origin['scheme'] === 'https' ? 'on' : 'off';
        $_SERVER['SERVER_PORT'] = (string) ($origin['port'] ?? ($origin['scheme'] === 'https' ? 443 : 80));
        $_SERVER['REQUEST_URI'] = rtrim($origin['path'] ?? '', '/') . '/';
        unset($config, $source);
        add_filter('pre_http_request', static function () {
            self::$guards['http']++;
            return new \WP_Error('a11_http_forbidden');
        }, PHP_INT_MAX);
        add_filter('pre_wp_mail', static function () {
            self::$guards['mail']++;
            return false;
        }, PHP_INT_MAX);
        add_filter('pre_schedule_event', static function () {
            self::$guards['scheduled']++;
            return false;
        }, PHP_INT_MAX);
        add_filter('pre_reschedule_event', static fn () => false, PHP_INT_MAX);
        add_filter('pre_unschedule_event', static fn () => false, PHP_INT_MAX);
        add_filter('pre_clear_scheduled_hook', static fn () => false, PHP_INT_MAX);
        add_filter('action_scheduler_allow_async_request_runner', '__return_false', PHP_INT_MAX);
        // No wp-load/config execution: only the native settings bootstrap with our fenced DB.
        require ABSPATH . 'wp-settings.php';
        if (is_multisite()) {
            throw new \RuntimeException('A11_MULTISITE_UNSUPPORTED');
        }
    }
}
