<?php

declare(strict_types=1);

define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
foreach (discoverT01Packages('/repo/wp')['packages'] as $package) {
    if ($package['relative'] !== 'plugins/imagine-site') {
        continue;
    }
    $dest = '/tmp/t01/plugins/imagine-site';
    copyTree('/repo/wp/plugins/imagine-site', $dest);
    copyTree('/opt/t01/' . $package['cacheKey'] . '/vendor', $dest . '/vendor');
    $cmd = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'PacksC28', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation'];
    $process = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
    exit(proc_close($process));
}
throw new RuntimeException('Paquet non découvert');
