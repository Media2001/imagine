<?php

declare(strict_types=1);

namespace Imagine\PublicAddresses;

final class RuntimeRefusal extends \RuntimeException
{
    public function __construct(string $code, public readonly array $details)
    {
        parent::__construct($code);
    }
}

final class Runtime
{
    public static array $guards = ['http' => 0, 'mail' => 0, 'scheduled' => 0];

    private const DROPINS = ['wp-content/db.php', 'wp-content/object-cache.php', 'wp-content/advanced-cache.php', 'wp-content/sunrise.php', 'wordfence-waf.php', '.user.ini'];

    public static function refusalMessage(\Throwable $error, string $code): string
    {
        // Site-controlled details are never output, even for future refusal types.
        if ($error instanceof RuntimeRefusal && $code === 'A11_DROPIN_UNSUPPORTED'
            && in_array($error->details['file'] ?? null, self::DROPINS, true)) {
            return $code . ' ' . json_encode(['file' => $error->details['file']], JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
        }
        return $code;
    }

    public static function validateConfiguration(string $source): void
    {
        $known = explode(' ', 'DB_NAME DB_USER DB_PASSWORD DB_HOST DB_CHARSET DB_COLLATE ABSPATH AUTH_KEY SECURE_AUTH_KEY LOGGED_IN_KEY NONCE_KEY AUTH_SALT SECURE_AUTH_SALT LOGGED_IN_SALT NONCE_SALT WP_DEBUG WP_DEBUG_LOG WP_DEBUG_DISPLAY WP_ENVIRONMENT_TYPE WP_HTTP_BLOCK_EXTERNAL DISABLE_WP_CRON AUTOMATIC_UPDATER_DISABLED WP_AUTO_UPDATE_CORE DISALLOW_FILE_MODS DISALLOW_FILE_EDIT WP_MEMORY_LIMIT WP_MAX_MEMORY_LIMIT WP_CACHE WP_POST_REVISIONS AUTOSAVE_INTERVAL EMPTY_TRASH_DAYS');
        $tokens = array_values(array_filter(token_get_all($source), static fn ($token): bool => !is_array($token) || !in_array($token[0], [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true)));
        foreach ($tokens as $index => $token) {
            if (is_array($token) && $token[0] === T_CONST) {
                throw new RuntimeRefusal('A11_CONFIG_OVERRIDE_UNSUPPORTED', []);
            }
            if (!is_array($token) || !in_array($token[0], [T_STRING, T_NAME_FULLY_QUALIFIED, T_NAME_QUALIFIED], true)
                || strtolower(ltrim($token[1], '\\')) !== 'define' || ($tokens[$index + 1] ?? '') !== '(') {
                continue;
            }
            $name = $tokens[$index + 2] ?? null;
            $constant = is_array($name) && $name[0] === T_CONSTANT_ENCAPSED_STRING ? substr($name[1], 1, -1) : '';
            if (!in_array($constant, $known, true)) {
                throw new RuntimeRefusal('A11_CONFIG_OVERRIDE_UNSUPPORTED', []);
            }
        }
    }

    public static function boot(string $site): void
    {
        $file = $site . '/wp-config.php';
        if (is_link($file) || realpath($file) !== $file || filesize($file) > 1048576) {
            throw new \RuntimeException('A11_CONFIG_UNSAFE');
        }
        $source = file_get_contents($file);
        $config = \Imagine\Audit\Audit::config($source);
        self::validateConfiguration($source);
        foreach (self::DROPINS as $dropin) {
            if (file_exists($site . '/' . $dropin) || is_link($site . '/' . $dropin)) {
                throw new RuntimeRefusal('A11_DROPIN_UNSUPPORTED', ['file' => $dropin]);
            }
        }
        foreach (new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($site, \FilesystemIterator::SKIP_DOTS), \RecursiveIteratorIterator::SELF_FIRST) as $path) {
            if ($path->isLink()) {
                throw new RuntimeRefusal('A11_SYMLINK_UNSUPPORTED', []);
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
