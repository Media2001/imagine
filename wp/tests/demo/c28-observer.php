<?php

declare(strict_types=1);

// Observateur temporaire, jamais de transport autorisé.
if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    return;
}
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http'] as $hook => $kind) {
    add_filter($hook, static function ($value) use ($kind) {
        $counts = get_option('imagine_c28_observations', []);
        $counts[$kind] = ($counts[$kind] ?? 0) + 1;
        update_option('imagine_c28_observations', $counts, false);
        return $value;
    }, -1000);
}
add_action('muplugins_loaded', static function (): void {
    add_filter('pre_http_request', static function ($value) {
        $counts = get_option('imagine_c28_observations', []);
        $key = is_wp_error($value) && $value->get_error_code() === 'imagine_demo_offline' ? 'http_blocked' : 'http_NOT_BLOCKED';
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        update_option('imagine_c28_observations', $counts, false);
        return $value;
    }, PHP_INT_MAX);
    add_filter('pre_wp_mail', static function ($value) {
        $counts = get_option('imagine_c28_observations', []);
        $key = $value === false ? 'mail_blocked' : 'mail_NOT_BLOCKED';
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        update_option('imagine_c28_observations', $counts, false);
        return $value;
    }, PHP_INT_MAX);
});
