<?php
declare(strict_types=1);
// Real PHPUnit in the existing offline image, package discovery unchanged.
define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
copyTree('/repo/wp/plugins/imagine-site', '/tmp/site');
copyTree('/opt/t01/imagine-site/vendor', '/tmp/site/vendor');
chdir('/tmp/site');
$args = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/junit.xml'];
if (($argv[1] ?? '') !== '') { $args[] = '--filter'; $args[] = $argv[1]; }
$p = proc_open($args, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes);
$exit = proc_close($p);
echo "\nC16_JUNIT\n";
if (is_file('/tmp/junit.xml')) { echo file_get_contents('/tmp/junit.xml'); }
exit($exit);
