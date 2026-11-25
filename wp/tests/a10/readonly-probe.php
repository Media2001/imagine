<?php

declare(strict_types=1);

define('IMAGINE_AUDIT_LIBRARY_ONLY', true);
require '/subject/audit';
require '/subject/a10/Projection.php';
require '/subject/a10/Inventory.php';
$subject = new Imagine\CouponInventory\Inventory(getenv('A10_SITE'));
$property = new ReflectionProperty($subject, 'db');
$db = $property->getValue($subject);
$blocked = false;
try {
    $db->exec("UPDATE wp_options SET option_value=option_value WHERE option_name='woocommerce_currency'");
} catch (PDOException $error) {
    $blocked = (int) ($error->errorInfo[1] ?? 0) === 1792;
}
echo json_encode(['blocked' => $blocked]) . "\n";
exit($blocked ? 0 : 1);
