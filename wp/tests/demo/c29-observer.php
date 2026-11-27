<?php
/** Sonde C29 temporaire : tout reste en mémoire dans la réponse, jamais en option/fichier. */
declare(strict_types=1);

if (($_GET['page'] ?? null) !== 'imagine-contact-brevo') {
    return;
}
$GLOBALS['imagine_c29_observe'] = ['entered' => false, 'finished' => false, 'sql' => [], 'http' => [], 'mail' => []];
$active = false;
ob_start(static function (string $body): string {
    return $body . '\n<!-- C29_OBSERVATION ' . base64_encode(wp_json_encode($GLOBALS['imagine_c29_observe'])) . ' -->';
});
add_filter('query', static function (string $sql) use (&$active): string {
    if ($active && !preg_match('/^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $sql)) {
        $GLOBALS['imagine_c29_observe']['sql'][] = strtok(trim($sql), ' ');
        throw new RuntimeException('C29 interdit une écriture pendant le rendu.');
    }
    return $sql;
}, PHP_INT_MAX);
add_filter('pre_http_request', static function ($pre) use (&$active) {
    if ($active) {
        $GLOBALS['imagine_c29_observe']['http'][] = 'blocked';
        return new WP_Error('c29_probe', 'HTTP bloqué avant transport');
    }
    return $pre;
}, PHP_INT_MAX);
add_filter('pre_wp_mail', static function ($pre) use (&$active) {
    if ($active) {
        $GLOBALS['imagine_c29_observe']['mail'][] = 'blocked';
        return false;
    }
    return $pre;
}, PHP_INT_MAX);
add_action('admin_menu', static function () use (&$active): void {
    $hook = get_plugin_page_hookname('imagine-contact-brevo', 'imagine');
    add_action($hook, static function () use (&$active): void {
        $active = true;
        $GLOBALS['imagine_c29_observe']['entered'] = true;
        if (($_GET['c29_witness'] ?? null) === '1') {
            try { update_option('imagine_c29_interdit', 'interdit', false); } catch (RuntimeException) {}
            wp_remote_get('https://example.invalid/');
            wp_mail('fictif@example.org', 'FICTIF', 'FICTIF');
        }
    }, PHP_INT_MIN);
    add_action($hook, static function () use (&$active): void {
        $GLOBALS['imagine_c29_observe']['finished'] = true;
        $active = false;
    }, PHP_INT_MAX);
}, PHP_INT_MAX);
