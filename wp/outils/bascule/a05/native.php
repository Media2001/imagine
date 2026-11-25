<?php

declare(strict_types=1);

namespace Imagine\Nettoyage;

try {
    ob_start();
    // Executes the exact A04 runtime safety probe, without any migration.
    require dirname(__DIR__) . '/a04/runtime.php';
    require_once ABSPATH . 'wp-admin/includes/plugin.php';
    $operation = json_decode((string) getenv('IMAGINE_A05_OPERATION'), true, 64, JSON_THROW_ON_ERROR);
    if ($operation['kind'] === 'preflight') {
        foreach ($operation['hooks'] as $hook) {
            if (has_action($hook) !== false) {
                throw new \RuntimeException('A05_CRON_NOT_ORPHAN:' . $hook);
            }
        }
    } else {
        $GLOBALS['imagine_a05_writes'] = $operation['kind'];
        $plugin = $operation['name'];
        if ($operation['kind'] === 'deactivate') {
            deactivate_plugins($plugin, true, false);
            if (is_plugin_active($plugin)) {
                throw new \RuntimeException('A05_DEACTIVATE_READBACK:' . $plugin);
            }
        } elseif ($operation['kind'] === 'uninstall') {
            if (is_uninstallable_plugin($plugin)) {
                uninstall_plugin($plugin);
            }
        } else {
            throw new \RuntimeException('A05_NATIVE_OPERATION');
        }
    }
    ob_end_clean();
    echo "A05_JSON={\"complete\":true}\n";
} catch (\Throwable $error) {
    while (ob_get_level()) {
        ob_end_clean();
    }
    $message = $error->getMessage();
    fwrite(STDERR, preg_match('/\AA05_[A-Z_]+(?::[A-Za-z0-9_.\/-]+)?\z/D', $message) ? $message . "\n" : "A05_NATIVE_FAILED\n");
    exit(1);
}
