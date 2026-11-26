<?php

declare(strict_types=1);

// With php -n and write/process functions disabled, prove the pure include seam.
if (($argv[1] ?? '') === '--pure') {
    ob_start();
    $checks = require '/repo/wp/tests/a19/unit.php';
    $output = ob_get_clean();
    if ($output !== '' || count($checks) !== 9 || in_array('FAIL', array_column($checks, 'status'), true)) {
        throw new RuntimeException('A19 pure include failed');
    }
    echo "A19_PURE_NO_EXTENSIONS_NO_WRITES_OK\n";
    return;
}

// Exercise the actual T01 discovery/coverage, without starting its global replay.
define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
$packages = discoverT01Packages('/work/wp')['packages'];
if (array_column($packages, 'relative') !== ['plugins/imagine-pilotage']) {
    throw new RuntimeException('A19 T01 package not discovered');
}
verifyCoverage('/work/wp/plugins/imagine-pilotage');
echo "A19_T01_DISCOVERY_OK\n";
