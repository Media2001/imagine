<?php

declare(strict_types=1);

// Disposable-fixture proof only. This is NOT an A-04 updater or a real-site entrypoint.
namespace Imagine\Staging;

require '/var/www/html/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/update.php';
require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';

$result = ['ok' => false, 'policy' => 'deployment_scripts_only'];
$owned = false;
$temp = null;
$directory = WP_PLUGIN_DIR . '/a01-script-capacity-only';
$file = $directory . '/hello.php';
$originalUser = get_current_user_id();
try {
    if (!defined('IMAGINE_STAGING_VERIFIED') || IMAGINE_STAGING_VERIFIED !== true
        || !preg_match('/^imagine-test-/', (string) getenv('A01_CAPACITY_SITE'))
        || wp_get_environment_type() !== 'staging' || !is_array(get_option('a01_paid_fixture'))
        || get_option('stylesheet') !== 'a01-fiction' || file_exists($directory)) {
        throw new \RuntimeException('CAPACITY_FIXTURE_REQUIRED');
    }
    $result['file_mods_locked'] = DISALLOW_FILE_MODS === true && DISALLOW_FILE_EDIT === true
        && !wp_is_file_mod_allowed('imagine-script-capacity');
    $administrator = get_user_by('login', 'imagine-test-admin');
    if (!$administrator) {
        throw new \RuntimeException('CAPACITY_ADMIN_REQUIRED');
    }
    wp_set_current_user($administrator->ID);
    $result['admin_updates_denied'] = !current_user_can('update_core') && !current_user_can('update_plugins')
        && !current_user_can('install_plugins') && !current_user_can('update_themes') && !current_user_can('edit_plugins');
    $result['auto_updates_disabled'] = AUTOMATIC_UPDATER_DISABLED === true && WP_AUTO_UPDATE_CORE === false
        && (new \WP_Automatic_Updater())->is_disabled();
    if (!$result['file_mods_locked'] || !$result['admin_updates_denied'] || !$result['auto_updates_disabled']
        || WP_HTTP_BLOCK_EXTERNAL !== true || WP_ACCESSIBLE_HOSTS !== '*.wordpress.org,*.woocommerce.com') {
        throw new \RuntimeException('CAPACITY_POLICY_REFUSED');
    }
    // Fixed public package, no licence, purchase, activation or commercial endpoint.
    $download = wp_remote_get('https://downloads.wordpress.org/plugin/hello-dolly.1.7.2.zip',
        ['timeout' => 30, 'limit_response_size' => 1048576, 'redirection' => 0]);
    if (is_wp_error($download)) {
        throw new \RuntimeException('CAPACITY_WORDPRESS_TRANSPORT_REFUSED');
    }
    $body = wp_remote_retrieve_body($download);
    $result['wordpress_download_http'] = wp_remote_retrieve_response_code($download);
    $result['wordpress_download_bytes'] = strlen($body);
    $result['wordpress_download_sha256'] = hash('sha256', $body);
    if ($result['wordpress_download_http'] !== 200
        || $result['wordpress_download_sha256'] !== '73847b0868f335d597c77a95aaa8c18eb1656c4b646e492ed1d65752d3236427') {
        throw new \RuntimeException('CAPACITY_PACKAGE_HASH_REFUSED');
    }
    $woo = wp_remote_get('https://developer.woocommerce.com/robots.txt',
        ['timeout' => 30, 'limit_response_size' => 65536, 'redirection' => 0]);
    if (is_wp_error($woo)) {
        throw new \RuntimeException('CAPACITY_WOOCOMMERCE_TRANSPORT_REFUSED');
    }
    $result['woocommerce_egress_http'] = wp_remote_retrieve_response_code($woo);
    if ($result['woocommerce_egress_http'] !== 200) {
        throw new \RuntimeException('CAPACITY_WOOCOMMERCE_HTTP_REFUSED');
    }
    // Closed local extraction of that pinned package. Never execute downloaded PHP.
    $temp = tempnam(sys_get_temp_dir(), 'a01-capacity-');
    if ($temp === false || file_put_contents($temp, $body) !== strlen($body)) {
        throw new \RuntimeException('CAPACITY_TEMP_REFUSED');
    }
    require_once ABSPATH . 'wp-admin/includes/class-pclzip.php';
    $entries = (new \PclZip($temp))->extract(PCLZIP_OPT_EXTRACT_AS_STRING);
    $php = null;
    foreach (is_array($entries) ? $entries : [] as $entry) {
        if ($entry['filename'] === 'hello-dolly/hello.php') {
            $php = $entry['content'];
        }
    }
    if (!is_string($php) || !str_contains($php, 'Plugin Name: Hello Dolly')) {
        throw new \RuntimeException('CAPACITY_PACKAGE_LAYOUT_REFUSED');
    }
    $plugins = get_option('active_plugins');
    if (!mkdir($directory, 0755)) {
        throw new \RuntimeException('CAPACITY_DIRECTORY_REFUSED');
    }
    $owned = true;
    $old = "<?php /* A01 inert rollback witness, never activated. */\n";
    if (file_put_contents($file, $old) !== strlen($old)) {
        throw new \RuntimeException('CAPACITY_BACKUP_REFUSED');
    }
    $backupHash = hash_file('sha256', $file);
    // Script deployment does not use an admin updater, override constants or WP-CLI.
    $deploy = static function () use ($file, $php): bool {
        return file_put_contents($file . '.next', $php) === strlen($php)
            && rename($file . '.next', $file) && hash_file('sha256', $file) === hash('sha256', $php);
    };
    $result['script_deploy_readback'] = $deploy();
    $firstHash = hash_file('sha256', $file);
    $result['script_replay_idempotent'] = $deploy() && hash_file('sha256', $file) === $firstHash;
    $result['deployed_php_sha256'] = $firstHash;
    $result['rollback_readback'] = file_put_contents($file, $old) === strlen($old)
        && hash_file('sha256', $file) === $backupHash && get_option('active_plugins') === $plugins;
    $result['downloaded_plugin_never_activated_or_executed'] = true;
    $result['commercial_download_not_tested'] = true;
    $result['ok'] = $result['script_deploy_readback'] && $result['script_replay_idempotent'] && $result['rollback_readback'];
} catch (\Throwable $exception) {
    $code = $exception instanceof \RuntimeException ? $exception->getMessage() : 'CAPACITY_PROBE_REFUSED';
    $result['failure_code'] = preg_match('/^CAPACITY_[A-Z_]+$/D', $code) ? $code : 'CAPACITY_PROBE_REFUSED';
} finally {
    wp_set_current_user($originalUser);
    if (is_string($temp) && file_exists($temp)) {
        unlink($temp);
    }
    if ($owned) {
        foreach ([$file . '.next', $file] as $path) {
            if (file_exists($path)) {
                unlink($path);
            }
        }
        rmdir($directory);
    }
    $result['owned_probe_files_absent'] = !file_exists($directory) && (!is_string($temp) || !file_exists($temp));
    $result['ok'] = $result['ok'] && $result['owned_probe_files_absent'];
}
echo 'A01_CAPACITY=' . json_encode($result, JSON_THROW_ON_ERROR) . "\n";
exit($result['ok'] ? 0 : 1);
