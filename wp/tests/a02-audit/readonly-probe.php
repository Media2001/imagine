<?php

declare(strict_types=1);

namespace Imagine\Audit\Tests;

define('IMAGINE_AUDIT_LIBRARY_ONLY', true);
require '/subject/audit';
$subject = new \Imagine\Audit\Audit((string) getenv('A02_SITE'));
$reflect = new \ReflectionClass($subject);
$db = $reflect->getProperty('db')->getValue($subject);
$blocked = false;
try {
    // UPDATE affects zero rows but must still be refused by the READ ONLY transaction.
    $db->exec("UPDATE wp_options SET option_value=option_value WHERE option_name='a02_no_such_option'");
} catch (\PDOException $error) {
    $blocked = $error->getCode() === '25006';
}
$projectionGuard = false;
try {
    $reflect->getMethod('query')->invoke($subject, 'DELETE FROM wp_options WHERE 1=0');
} catch (\RuntimeException $error) {
    $projectionGuard = $error->getMessage() === 'A02_NON_SELECT_FORBIDDEN';
}
echo json_encode(['transaction_write_blocked' => $blocked, 'query_non_select_blocked' => $projectionGuard]) . "\n";
exit($blocked && $projectionGuard ? 0 : 1);
