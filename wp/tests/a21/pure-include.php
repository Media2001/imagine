<?php

declare(strict_types=1);

$before = [];
foreach (glob('/report/*') as $file) {
    if (is_file($file)) {
        $before[$file] = hash_file('sha256', $file);
    }
}
ob_start();
$checks = require __DIR__ . '/unit.php';
$noise = ob_get_clean();
$after = [];
foreach (glob('/report/*') as $file) {
    if (is_file($file)) {
        $after[$file] = hash_file('sha256', $file);
    }
}
echo json_encode([
    'count' => count($checks),
    'green' => !in_array('FAIL', array_column($checks, 'status'), true),
    'quiet' => $noise === '',
    'files_unchanged' => $before === $after,
    'native_absent' => !function_exists('WC') && !class_exists('Imagine\\PublicAddresses\\Runtime', false),
], JSON_THROW_ON_ERROR) . "\n";
