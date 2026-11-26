<?php

declare(strict_types=1);

require '/subject/a12/AuditLibrary.php';
\Imagine\ContentInventory\AuditLibrary::load();
require '/subject/a11/Runtime.php';
require '/subject/a12/Registry.php';
require '/subject/a12/Inventory.php';
ob_start();
$inventory = new \Imagine\ContentInventory\Inventory(getenv('A12_SITE'));
$db = $GLOBALS['wpdb'];
$property = new ReflectionProperty($inventory, 'db');
$sameSession = $property->getValue($inventory) === $db;
$blocked = $db->query('UPDATE wp_posts SET ID=ID WHERE 1=0') === false;
$escape = $db->query('COMMIT') === false && $db->query('SET SESSION TRANSACTION READ WRITE') === false;
$server = @mysqli_query($db->dbh, 'UPDATE wp_posts SET ID=ID WHERE 1=0') === false && mysqli_errno($db->dbh) === 1792;
$http = wp_remote_get('https://must-not-connect.invalid/');
$mail = wp_mail('fiction@example.org', 'A12', 'A12');
$scheduled = wp_schedule_single_event(time() + 999, 'a12_must_not_schedule');
$guards = \Imagine\PublicAddresses\Runtime::$guards;
$report = $inventory->collect();
$results = [
    'blocked' => $blocked, 'server_readonly' => $server, 'escape_denied' => $escape,
    'same_session_for_registry_metadata_attachments' => $sameSession && $GLOBALS['wpdb'] === $db
        && $report['registry']['runtime_verified'],
    'http_denied' => is_wp_error($http), 'mail_denied' => $mail === false, 'schedule_denied' => $scheduled === false,
    'guards_exercised' => $guards['http'] >= 1 && $guards['mail'] >= 1 && $guards['scheduled'] >= 1,
    'early_bootstrap_guards_all_pass' => count($GLOBALS['a12_early_guards'] ?? []) === 9
        && !in_array(false, $GLOBALS['a12_early_guards'], true),
];
$site = getenv('A12_SITE');
$index = $site . '/index.php';
$before = hash_file('sha256', $index);
$results['site_create'] = @file_put_contents($site . '/a12-create-must-fail', 'X') === false;
$results['site_truncate'] = @file_put_contents($index, 'A12_TRUNCATE_MUST_FAIL') === false
    && hash_file('sha256', $index) === $before;
$results['site_rename'] = @rename($index, $site . '/a12-rename-must-fail') === false;
$results['site_unlink'] = @unlink($index) === false;
$results['site_mkdir'] = @mkdir($site . '/a12-mkdir-must-fail') === false;
ob_end_clean();
echo json_encode($results, JSON_THROW_ON_ERROR) . "\n";
exit(in_array(false, $results, true) ? 1 : 0);
