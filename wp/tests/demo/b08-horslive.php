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
    verifyCoverage($dest);
    $cmd = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'Cooperative|Soutenir|Sujet', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/b08-junit.xml'];
    $process = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
    $exit = proc_close($process);
    echo "B08 JUNIT BEGIN\n", file_get_contents('/tmp/b08-junit.xml'), "B08 JUNIT END\n";
    exit($exit);
}
throw new RuntimeException('Paquet non découvert');
