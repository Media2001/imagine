<?php

declare(strict_types=1);

define('IMAGINE_AUDIT_LIBRARY_ONLY', true);
require '/subject/audit';
require '/subject/a12/Declarations.php';
require '/subject/a12/Inventory.php';
$inventory = new \Imagine\ContentInventory\Inventory(getenv('A12_SITE'));
$property = new ReflectionProperty($inventory, 'db');
$db = $property->getValue($inventory);
$blocked = false;
try {
    $db->exec('UPDATE wp_posts SET ID=ID WHERE 1=0');
} catch (PDOException $exception) {
    $blocked = ($exception->errorInfo[1] ?? null) === 1792;
}
echo json_encode(['blocked' => $blocked], JSON_THROW_ON_ERROR) . "\n";
exit($blocked ? 0 : 1);
