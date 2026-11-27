<?php

// phpcs:disable PSR1.Files.SideEffects.FoundWithSymbols
// Executable fixture mode flag plus shared assertions, not a reusable symbol library.
declare(strict_types=1);

// The executable fixture intentionally defines its mode before including the shared test script.
// phpcs:ignore PSR1.Files.SideEffects.FoundWithSymbols
define('A31_PURE_PROBE', true);
require '/opt/a31/unit.php';
echo 'A31_PURE_OK ' . count($checks) . "\n";
