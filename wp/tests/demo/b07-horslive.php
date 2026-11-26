<?php

declare(strict_types=1);

// Rejeu ciblé dans la même image, sans réseau, sans WordPress ni site.
define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
$discovery = discoverT01Packages('/repo/wp');
foreach ($discovery['packages'] as $package) {
    if ($package['relative'] !== 'plugins/imagine-site') { continue; }
    $source = '/repo/wp/' . $package['relative'];
    $dest = '/tmp/t01/' . $package['relative'];
    copyTree($source, $dest);
    copyTree('/opt/t01/' . $package['cacheKey'] . '/vendor', $dest . '/vendor');
    // Les gabarits et le filtre sont les vrais fichiers du thème.
    copyTree('/repo/wp/themes/imagine', '/tmp/t01/themes/imagine');
    verifyCoverage($dest);
    $cmd = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'Agenda', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/agenda-junit.xml'];
    $proc = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
    $code = proc_close($proc);
    echo "B07 JUNIT BEGIN\n", file_get_contents('/tmp/agenda-junit.xml'), "B07 JUNIT END\n";
    exit($code);
}
throw new RuntimeException('Paquet imagine-site non découvert');
