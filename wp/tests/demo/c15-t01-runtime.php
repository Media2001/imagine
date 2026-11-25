<?php
/** Runs only in an owned, disconnected T01 container. */
declare(strict_types=1);
define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
$discovery = discoverT01Packages('/repo/wp');
$found = array_filter($discovery['packages'], static fn ($r) => $r['relative'] === 'plugins/imagine-site');
if (count($found) !== 1) {
    throw new RuntimeException('C15 package not discovered');
}
copyTree('/repo/wp/plugins/imagine-site', '/tmp/site');
copyTree('/opt/t01/imagine-site/vendor', '/tmp/site/vendor');
verifyCoverage('/tmp/site');
chdir('/tmp/site');
$args = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--do-not-cache-result',
    '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/junit.xml'];
if (($argv[1] ?? '') !== '') {
    $args[] = '--filter';
    $args[] = $argv[1];
}
$process = proc_open($args, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes);
$exit = proc_close($process);
echo "\nC15_JUNIT\n";
if (is_file('/tmp/junit.xml')) {
    echo file_get_contents('/tmp/junit.xml');
}
exit($exit);
