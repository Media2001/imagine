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
        'slash' => ['Contact.php', "'meta_input' => wp_slash(\$meta)", "'meta_input' => \$meta"],
        'consentement' => ['Contact.php', 'type="checkbox" name="consentement"', 'type="checkbox" checked name="consentement"'],
        'mail' => ['Contact.php', '$meta = [', "wp_mail('fictif@example.org', 'Mutation', 'Fictif');\n        \$meta = ["],
        'http' => ['Contact.php', '$meta = [', "wp_remote_get('https://example.org/');\n        \$meta = ["],
        'prive' => ['Contact.php', "'post_status' => 'private'", "'post_status' => 'publish'"],
        'rest' => ['Contact.php', "'show_in_rest' => false", "'show_in_rest' => true"],
        'export' => ['ContactConfidentialite.php', "return ['data' => \$data,", "return ['data' => [],"],
        'effacement' => ['ContactConfidentialite.php', 'wp_delete_post($id, true)', 'true'],
        'lecture' => ['Contact.php', "\$wpdb->last_error !== '' ? null", "\$wpdb->last_error !== '' ? []"],
        'nonce' => ['Contact.php', "&& wp_verify_nonce(wp_unslash(\$post['_b09']), 'imagine_contact')", '&& true'],
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
        echo 'B09 SOURCE MUTANT ', $mutation, "\n";
    }
    verifyCoverage($dest);
    $cmd = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'Contact', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/b09-junit.xml'];
    $process = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
    $exit = proc_close($process);
    echo "B09 JUNIT BEGIN\n", file_get_contents('/tmp/b09-junit.xml'), "B09 JUNIT END\n";
    exit($exit);
}
throw new RuntimeException('Paquet non découvert');
