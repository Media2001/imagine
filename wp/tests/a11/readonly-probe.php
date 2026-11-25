<?php

declare(strict_types=1);

define('IMAGINE_AUDIT_LIBRARY_ONLY', true);
require '/subject/audit';
require '/subject/a11/Runtime.php';
ob_start();
Imagine\PublicAddresses\Runtime::boot(getenv('A11_SITE'));
global $wpdb;
$before = $wpdb->get_var("SELECT option_value FROM {$wpdb->options} WHERE option_name='woocommerce_currency'");
$blocked = $wpdb->query("UPDATE {$wpdb->options} SET option_value='A11_WRITE_CANARY' WHERE option_name='woocommerce_currency'") === false;
$transactionBlocked = $wpdb->query('COMMIT') === false && $wpdb->query('SET SESSION TRANSACTION READ WRITE') === false;
$same = $before === $wpdb->get_var("SELECT option_value FROM {$wpdb->options} WHERE option_name='woocommerce_currency'");
$http = wp_remote_get('https://must-not-connect.invalid/');
$mail = wp_mail('fiction@example.org', 'A11', 'A11');
$scheduled = wp_schedule_single_event(time() + 999, 'a11_must_not_schedule');
$guards = Imagine\PublicAddresses\Runtime::$guards;
ob_end_clean();
echo json_encode(['write_denied' => $blocked, 'escape_denied' => $transactionBlocked, 'unchanged' => $same, 'http_denied' => is_wp_error($http), 'mail_denied' => $mail === false, 'schedule_denied' => $scheduled === false, 'guards_exercised' => $guards['http'] >= 1 && $guards['mail'] >= 1 && $guards['scheduled'] >= 1]) . "\n";
