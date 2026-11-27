<?php

declare(strict_types=1);

define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
foreach (discoverT01Packages('/repo/wp')['packages'] as $package) {
    if ($package['relative'] !== 'plugins/imagine-site') {
        continue;
    }
    $names = ['Contact.php', 'ContactConfidentialite.php', 'AutresPages.php'];
    $out = [];
    foreach ($names as $name) {
        $path = '/tmp/' . $name;
        copy('/repo/wp/plugins/imagine-site/' . $name, $path);
        $cmd = ['php', '/opt/t01/' . $package['cacheKey'] . '/vendor/bin/phpcbf', '--standard=PSR12', $path];
        $p = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']], $pipes);
        stream_get_contents($pipes[1]);
        stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        $exit = proc_close($p);
        if ($exit > 1) {
            throw new RuntimeException('Formatage B09 refusé');
        }
        $out[$name] = file_get_contents($path);
    }
    echo json_encode($out, JSON_THROW_ON_ERROR);
    exit;
}
throw new RuntimeException('Paquet absent');
