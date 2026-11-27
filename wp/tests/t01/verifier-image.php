<?php

declare(strict_types=1);

try {
    foreach (['dom', 'SimpleXML', 'mbstring', 'xml', 'xmlwriter'] as $extension) {
        if (!extension_loaded($extension)) {
            throw new RuntimeException('Required PHP extension absent: ' . $extension);
        }
    }
    if (!is_executable('/usr/bin/python3')) {
        throw new RuntimeException('Python T03 absent; run preparer-image.ps1.');
    }
    $python = proc_open(
        ['/usr/bin/python3', '-B', '-c', 'import hashlib,json,pathlib,subprocess,sys; assert sys.version_info >= (3, 9)'],
        [0 => ['file', '/dev/null', 'r'], 1 => ['file', '/dev/null', 'w'], 2 => ['file', '/dev/null', 'w']],
        $pythonPipes,
        '/tmp'
    );
    if (!is_resource($python) || proc_close($python) !== 0) {
        throw new RuntimeException('Python T03 incomplete; run preparer-image.ps1.');
    }
    echo "T03 IMAGE PYTHON : offline standard-library probe PASS\n";
    $packages = glob('/opt/t01/*/composer.json');
    if ($packages === []) {
        throw new RuntimeException('No dependency package in image.');
    }
    foreach ($packages as $manifest) {
        $directory = dirname($manifest);
        foreach (['composer.lock', 'vendor/autoload.php', 'vendor/bin/phpunit'] as $required) {
            if (!is_readable($directory . '/' . $required)) {
                throw new RuntimeException('Missing prepared dependency: ' . $directory . '/' . $required);
            }
        }
        echo 'T01 IMAGE PACKAGE : ' . basename($directory) . '; lock=' . hash_file('sha256', $directory . '/composer.lock') . "\n";
    }
    echo 'T01 IMAGE READY : PHP ' . PHP_VERSION . '; ' . count($packages) . " packages; no site or commercial extension\n";
} catch (Throwable $error) {
    fwrite(STDERR, 'T01 IMAGE ERROR : ' . $error->getMessage() . "\n");
    exit(1);
}
