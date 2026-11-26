<?php

declare(strict_types=1);

// Invoked with php -n and disabled write/process functions, without a WordPress tree.
$checks = require '/opt/a20/unit.php';
if (!is_array($checks) || $checks === [] || in_array('FAIL', array_column($checks, 'status'), true)) {
    exit(1);
}
echo 'A20_PURE_OK ' . count($checks) . "\n";
