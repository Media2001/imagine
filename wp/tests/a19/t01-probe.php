<?php

declare(strict_types=1);

// Exercise the actual T01 discovery/coverage, without starting its global replay.
define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
$packages = discoverT01Packages('/work/wp')['packages'];
if (array_column($packages, 'relative') !== ['plugins/imagine-pilotage']) {
    throw new RuntimeException('A19 T01 package not discovered');
}
verifyCoverage('/work/wp/plugins/imagine-pilotage');
echo "A19_T01_DISCOVERY_OK\n";
