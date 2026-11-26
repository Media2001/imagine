<?php

declare(strict_types=1);

putenv('A26_PURE_INCLUDE=1');
require '/opt/a26/unit.php';
if ($result['exit_code'] !== 0) {
    exit(1);
}
echo 'A26_PURE_OK ' . count($checks) . "\n";
