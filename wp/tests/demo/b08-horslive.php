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
        'slash' => ['Sujet.php', "'meta_input' => wp_slash(\$meta)", "'meta_input' => \$meta"],
        'https' => ['Soutenir.php', "parse_url(\$url, PHP_URL_SCHEME) === 'https'", "in_array(parse_url(\$url, PHP_URL_SCHEME), ['https', 'http'], true)"],
        'don' => ['Soutenir.php', "if (\$config['don']) {", 'if (true) {'],
        'parts' => ['Soutenir.php', 'rel="sponsored"', 'rel="nofollow"'],
        'consentement' => ['Sujet.php', 'type="checkbox" name="consentement"', 'type="checkbox" checked name="consentement"'],
        'mail' => ['Sujet.php', '$meta = [', "wp_mail('fictif@example.org', 'Mutation', 'Fictif');\n        \$meta = ["],
        'http' => ['Sujet.php', '$meta = [', "wp_remote_get('https://example.org/');\n        \$meta = ["],
        'prive' => ['Sujet.php', "'post_status' => 'private'", "'post_status' => 'publish'"],
        'rest' => ['Sujet.php', "'show_in_rest' => false", "'show_in_rest' => true"],
        'public' => ['Sujet.php', "'public' => false", "'public' => true"],
        'export' => ['SujetConfidentialite.php', "return ['data' => \$data,", "return ['data' => [],"],
        'effacement' => ['SujetConfidentialite.php', 'wp_delete_post($id, true)', 'true'],
        'lecture' => ['Sujet.php', "\$wpdb->last_error !== '' ? null", "\$wpdb->last_error !== '' ? []"],
        'nonce' => ['Sujet.php', "&& wp_verify_nonce(wp_unslash(\$post['_b08']), 'imagine_sujet')", '&& true'],
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
        echo 'B08 SOURCE MUTANT ', $mutation, "\n";
    }
    verifyCoverage($dest);
    $cmd = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'Cooperative|Soutenir|Sujet', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/b08-junit.xml'];
    $process = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
    $exit = proc_close($process);
    echo "B08 JUNIT BEGIN\n", file_get_contents('/tmp/b08-junit.xml'), "B08 JUNIT END\n";
    exit($exit);
}
throw new RuntimeException('Paquet non découvert');
