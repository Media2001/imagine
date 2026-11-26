<?php

declare(strict_types=1);

putenv('A27_PURE_INCLUDE=1');
require '/opt/a27/unit.php';
if ($result['exit_code'] !== 0) {
    exit(1);
}
echo 'A27_PURE_OK ' . count($checks) . "\n";
