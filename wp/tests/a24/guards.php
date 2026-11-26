<?php

// Fixture probes run inside the subject's actual kernel fence and SQL transaction.
if (getenv('A24_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH . 'wp-includes/pluggable.php';
    add_action('plugins_loaded', static function () {
        if (
            as_enqueue_async_action('a24_forbidden') !== 0
            || as_schedule_single_action(time() + 9999, 'a24_forbidden') !== 0
            || as_schedule_recurring_action(time() + 9999, 3600, 'a24_forbidden') !== 0
            || as_schedule_cron_action(time() + 9999, '* * * * *', 'a24_forbidden') !== 0
        ) {
            throw new RuntimeException('A24_AS_GUARD_PRIVATE_CANARY');
        }
    }, PHP_INT_MAX);
    if (
        $wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @mysqli_query($wpdb->dbh, 'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @file_put_contents(ABSPATH . 'forbidden', 'NO') !== false
        || @file_put_contents(ABSPATH . 'a24-write-canary', 'NO') !== false
        || @fopen(ABSPATH . 'a24-write-canary', 'wb') !== false
        || @rename(ABSPATH . 'a24-write-canary', ABSPATH . 'forbidden') !== false
        || @unlink(ABSPATH . 'a24-write-canary') !== false
        || @mkdir(ABSPATH . 'forbidden-dir') !== false
        || wp_mail('fictif@example.org', 'A24_MAIL_PRIVATE_CANARY', 'A24_MAIL_PRIVATE_CANARY') !== false
        || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
        || wp_schedule_single_event(time() + 9999, 'a24_forbidden') !== false
        || function_exists('mail') || function_exists('exec')
    ) {
        throw new RuntimeException('A24_EARLY_GUARD_PRIVATE_CANARY');
    }
    echo 'A24_DISPLAY_PRIVATE_CANARY';
}
