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
    $mutation = $argv[1] ?? '';
    if ($mutation !== '') {
        $mutants = [
            'avant-paiement' => ['AcquisitionRegles.php', '$paid && $dated', 'true'],
            'tiers' => ['AcquisitionRegles.php', '$actor === $owner', 'true'],
            'operateur' => ['AcquisitionRegles.php', "\$via !== 'imagine-c16'", 'true'],
            'source-ecrasee' => ['Acquisition.php', "get_user_meta(\$actor, self::SOURCE, true) === ''", 'true'],
            'export' => ['AcquisitionConfidentialite.php', "'data' => array_slice(\$data, (max(1, \$page) - 1) * 50, 50)", "'data' => []"],
            'effacement' => ['AcquisitionConfidentialite.php', 'update_option($key, $tombstone, false);', '// effacement retiré'],
            'export-tiers' => ['AcquisitionConfidentialite.php', '$owner === null || $data[\'compte\'] === $owner', 'true'],
            'reglage-invalide' => ['AcquisitionReglages.php', 'return Acquisition::configuration();', 'return [];'],
        ];
        if (!isset($mutants[$mutation])) {
            throw new RuntimeException('Mutation inconnue');
        }
        [$file, $old, $new] = $mutants[$mutation];
        $path = $dest . '/' . $file;
        $raw = file_get_contents($path);
        if (substr_count($raw, $old) !== 1) {
            throw new RuntimeException('Cible ambiguë');
        }
        file_put_contents($path, str_replace($old, $new, $raw));
        echo 'C27 SOURCE MUTANT ', $mutation, "\n";
    }
    $process = proc_open(['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'Acquisition', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation'], [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
    exit(proc_close($process));
}
throw new RuntimeException('Paquet absent');
