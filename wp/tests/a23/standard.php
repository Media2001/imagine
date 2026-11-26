<?php

declare(strict_types=1);

// Source inspection only: no WordPress bootstrap and no password check.
$root = '/opt/wordpress/wordpress/wp-includes/';
$source = file_get_contents($root . 'pluggable.php');
$phpass = file_get_contents($root . 'class-phpass.php');
$version = file_get_contents($root . 'version.php');
preg_match('/\$wp_version\s*=\s*\'([^\']+)\'/', $version, $m);
$checks = [
    'native_user_pass_storage' => preg_match('/\'user_pass\'\s*=>\s*\$hashed/', $source) === 1,
    'legacy_md5_branch' => str_contains($source, 'strlen( $hash ) <= 32')
        && str_contains($source, 'hash_equals( $hash, md5( $password ) )'),
    'overridden_hasher' => str_contains($source, '$wp_hasher->CheckPassword( $password, $hash )'),
    'wordpress_prefixed_branch' => str_contains($source, "str_starts_with( \$hash, '\$wp' )"),
    'sha384_hmac' => str_contains($source, "hash_hmac( 'sha384', \$password, 'wp-sha384', true )"),
    'phpass_branch' => str_contains($source, "str_starts_with( \$hash, '\$P\$' )"),
    'compat_password_verify' => str_contains($source, 'password_verify( $password, $hash )'),
    'default_bcrypt_filter' => str_contains($source, "apply_filters( 'wp_hash_password_algorithm', PASSWORD_BCRYPT )"),
    'phpass_p_and_h_recognition' => preg_match('/\$id\s*!==?\s*\'\$P\$\'\s*&&\s*\$id\s*!==?\s*\'\$H\$\'/', $phpass) === 1,
];
$report = ['wordpress' => $m[1] ?? null, 'source_sha256' => [
    'wp-includes/pluggable.php' => hash('sha256', $source),
    'wp-includes/class-phpass.php' => hash('sha256', $phpass),
    'wp-includes/version.php' => hash('sha256', $version)],
    'checks' => array_map(static fn(string $key, bool $ok): array => [
        'check' => $key, 'status' => $ok ? 'PASS' : 'FAIL'
    ], array_keys($checks), array_values($checks)),
    'no_password_check_executed' => true, 'exit_code' => (int) in_array(false, $checks, true)];
file_put_contents('/report/standard.json', json_encode($report, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
exit($report['exit_code']);
