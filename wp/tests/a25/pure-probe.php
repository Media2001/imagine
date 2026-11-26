<?php

declare(strict_types=1);

putenv('A25_PURE_INCLUDE=1');
require '/opt/a25/unit.php';
if ($result['exit_code'] !== 0) {
    exit(1);
}
echo 'A25_PURE_OK ' . count($checks) . "\n";
