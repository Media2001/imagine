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
    $mutants = [
        'delai' => ['RetractationRegles.php', '$now <= $end', 'true'],
        'proprietaire' => ['Retractation.php', 'if (!$order || $user < 1 || $order->get_customer_id() !== $user) {', 'if (!$order || $user < 1) {'],
        'confirmation' => ['Retractation.php', "\$confirmation !== 'confirmer'", 'false'],
        'doublon' => ['Retractation.php', 'if ($existing !== null) {', 'if (false) {'],
        'export' => ['RetractationConfidentialite.php', "'data' => \$data,", "'data' => [],"],
        'effacement' => ['RetractationConfidentialite.php', 'wp_delete_comment((int)$row[\'note\'], true)', 'true'],
        'mail' => ['Retractation.php', '$note = (int)$order->add_order_note(', "wp_mail('fictif@example.org', 'Mutation', 'Fictif');\n            \$note = (int)\$order->add_order_note("],
        'financier' => ['Retractation.php', '$note = (int)$order->add_order_note(', "\$order->update_status('cancelled');\n            \$note = (int)\$order->add_order_note("],
        'export-tiers' => ['RetractationConfidentialite.php', '$owner === null || (int)$data[\'compte\'] === $owner', 'true'],
        'nonce' => ['Retractation.php', "\$step !== '' && !wp_verify_nonce(", "false && !wp_verify_nonce("],
        'http' => ['Retractation.php', '$note = (int)$order->add_order_note(', "wp_remote_get('https://example.org/');\n            \$note = (int)\$order->add_order_note("],
    ];
    if ($mutation !== '') {
        if (!isset($mutants[$mutation])) {
            throw new RuntimeException('Mutation inconnue');
        }
        [$name, $old, $new] = $mutants[$mutation];
        $path = $dest . '/' . $name;
        $raw = file_get_contents($path);
        if (substr_count($raw, $old) !== 1) {
            throw new RuntimeException('Cible mutation ambiguë : ' . $mutation);
        }
        file_put_contents($path, str_replace($old, $new, $raw));
        echo 'C25 SOURCE MUTANT ', $mutation, "\n";
    }
    verifyCoverage($dest);
    $cmd = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'Retractation', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/c25-junit.xml'];
    $process = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
    $exit = proc_close($process);
    echo "C25 JUNIT BEGIN\n", file_get_contents('/tmp/c25-junit.xml'), "C25 JUNIT END\n";
    exit($exit);
}
throw new RuntimeException('Paquet non découvert');
