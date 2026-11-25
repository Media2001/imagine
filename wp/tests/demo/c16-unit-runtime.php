<?php
declare(strict_types=1);
// Existing image supplies dependencies; source siblings stay under /repo/wp.
$args = ['php', '/opt/t01/imagine-site/vendor/bin/phpunit',
    '--configuration', '/repo/wp/plugins/imagine-site/phpunit.xml',
    '--bootstrap', '/repo/wp/tests/demo/b04-unit-bootstrap.php',
    '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/junit.xml'];
if (($argv[1] ?? '') !== '') { $args[] = '--filter'; $args[] = $argv[1]; }
$p = proc_open($args, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes);
$exit = proc_close($p);
echo "\nC16_JUNIT\n";
if (is_file('/tmp/junit.xml')) { echo file_get_contents('/tmp/junit.xml'); }
exit($exit);
