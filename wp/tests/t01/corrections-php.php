<?php

declare(strict_types=1);

// Executable regression suite: run only in the disposable T01 Docker image.
if (PHP_OS_FAMILY !== 'Linux' || !is_file('/.dockerenv') || !is_dir('/opt/t01')) {
    fwrite(STDERR, "T01 corrections require the disposable Linux Docker image.\n");
    exit(1);
}

$executer = __DIR__ . '/executer.php';
$failures = 0;
$tests = 0;

function correction(string $name, callable $test): void
{
    global $failures, $tests;
    $tests++;
    try {
        $test();
        echo "PASS $name\n";
    } catch (Throwable $error) {
        $failures++;
        echo "FAIL $name : " . $error->getMessage() . "\n";
    }
}

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

function childPhp(string $code): array
{
    $process = proc_open(['php', '-r', $code], [0 => ['file', '/dev/null', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']], $pipes);
    check(is_resource($process), 'Cannot start isolated PHP child');
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    return [proc_close($process), $stdout . $stderr];
}

correction('executor has a function-only include', static function () use ($executer): void {
    [$code, $output] = childPhp('define("T01_FUNCTIONS_ONLY", true); require ' . var_export($executer, true) . '; echo "FUNCTIONS_ONLY_OK";');
    check($code === 0 && $output === 'FUNCTIONS_ONLY_OK', 'Function-only include did not return without replay: ' . $output);
});

define('T01_FUNCTIONS_ONLY', true);
require $executer;

function packageFixture(string $suite, string $rootAttributes = '', string $extra = '', string $config = 'phpunit.xml'): string
{
    $path = '/tmp/t01-correction-' . bin2hex(random_bytes(6));
    mkdir($path . '/tests/nested', 0777, true);
    file_put_contents($path . '/tests/AlphaTest.php', '<?php');
    file_put_contents($path . '/tests/nested/BetaTest.php', '<?php');
    file_put_contents($path . '/' . $config, '<phpunit bootstrap="vendor/autoload.php" ' . $rootAttributes . '><testsuites><testsuite name="All">' . $suite . '</testsuite></testsuites>' . $extra . '</phpunit>');
    return $path;
}

function rejected(callable $operation, string $message): void
{
    try {
        $operation();
    } catch (RuntimeException $error) {
        return;
    }
    throw new RuntimeException($message);
}

correction('full directory selection is accepted', static function (): void {
    verifyCoverage(packageFixture('<directory>tests</directory>'));
});

foreach ([
    'exclude directory' => ['<directory>tests</directory><exclude>tests/nested</exclude>', '', ''],
    'directory suffix' => ['<directory suffix="AlphaTest.php">tests</directory>', '', ''],
    'directory prefix' => ['<directory prefix="Alpha">tests</directory>', '', ''],
    'directory PHP version' => ['<directory phpVersion="99.0" phpVersionOperator=">=">tests</directory>', '', ''],
    'file PHP version' => ['<file phpVersion="99.0">tests/AlphaTest.php</file><file>tests/nested/BetaTest.php</file>', '', ''],
    'default test suite' => ['<directory>tests</directory>', 'defaultTestSuite="Elsewhere"', ''],
    'group filter' => ['<directory>tests</directory>', '', '<groups><exclude><group>slow</group></exclude></groups>'],
    'stop early' => ['<directory>tests</directory>', 'stopOnFailure="true"', ''],
    'unknown selector' => ['<directory>tests</directory><filter>Alpha</filter>', '', ''],
] as $name => [$suite, $attributes, $extra]) {
    correction('refuses ' . $name, static function () use ($suite, $attributes, $extra): void {
        $path = packageFixture($suite, $attributes, $extra);
        rejected(static fn () => verifyCoverage($path), 'Partial/unsupported PHPUnit selection was accepted');
    });
}

correction('phpunit.xml.dist is supported', static function (): void {
    verifyCoverage(packageFixture('<directory>tests</directory>', '', '', 'phpunit.xml.dist'));
});

correction('xml takes precedence over xml.dist', static function (): void {
    $path = packageFixture('<directory>tests</directory><exclude>tests/nested</exclude>');
    file_put_contents($path . '/phpunit.xml.dist', '<phpunit bootstrap="vendor/autoload.php"><testsuites><testsuite name="All"><directory>tests</directory></testsuite></testsuites></phpunit>');
    rejected(static fn () => verifyCoverage($path), 'Excluded active phpunit.xml was bypassed by dist');
});

echo "T01 CORRECTIONS : $tests tests, $failures failures\n";
exit($failures === 0 ? 0 : 1);
