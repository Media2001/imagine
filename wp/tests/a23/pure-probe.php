<?php

declare(strict_types=1);

$checks = require __DIR__ . '/unit.php';
if (!is_array($checks) || !$checks || in_array('FAIL', array_column($checks, 'status'), true)) {
    exit(1);
}
echo 'A23_PURE_OK ' . count($checks) . "\n";
