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

function fixtureReplay(string $methodBody, string $configuration = 'phpunit.xml', string $kind = 'plugins', string $selection = '<directory>tests</directory>', bool $manifests = true): array
{
    $root = '/tmp/t01-replay-' . bin2hex(random_bytes(6));
    $package = $root . '/wp/' . $kind . '/imagine-pilotage';
    mkdir($package . '/tests', 0777, true);
    mkdir($root . '/wp/plugins/untested', 0777, true);
    mkdir($root . '/cache', 0777, true);
    $cacheKey = $kind === 'plugins' ? 'imagine-pilotage' : $kind . '--imagine-pilotage';
    symlink('/opt/t01/imagine-pilotage', $root . '/cache/' . $cacheKey);
    foreach (['composer.json', 'composer.lock'] as $file) {
        if ($manifests) {
            copy('/opt/t01/imagine-pilotage/' . $file, $package . '/' . $file);
        }
    }
    file_put_contents($package . '/' . $configuration, '<phpunit bootstrap="vendor/autoload.php"><testsuites><testsuite name="Synthetic">' . $selection . '</testsuite></testsuites></phpunit>');
    file_put_contents($package . '/tests/SyntheticTest.php', '<?php final class SyntheticTest extends \\PHPUnit\\Framework\\TestCase { public function testSynthetic(): void { ' . $methodBody . ' } }');
    // Relocate only hard-coded input/output roots; selection and verdict code are unchanged.
    $code = str_replace(['/repo/wp', '/tmp/t01/', '/opt/t01/', '/tmp/t01-tools'], [$root . '/wp', $root . '/work/', $root . '/cache/', $root . '/tools-work'], file_get_contents(__DIR__ . '/executer.php'));
    file_put_contents($root . '/executer.php', $code);
    // The relocated executor includes the packet phase too; copy its real
    // dependencies instead of adding a production bypass or editing verdicts.
    foreach (['discovery.php', 'tools.php', 'paquets.php', 'paquets.py'] as $file) {
        copy(__DIR__ . '/' . $file, $root . '/' . $file);
    }
    [$status, $output] = childPhp('require ' . var_export($root . '/executer.php', true) . ';');
    check(preg_match('/^T01_RESULT (.+)$/m', $output, $matches) === 1, 'Replay result missing: ' . $output);
    return [$status, json_decode($matches[1], true, 512, JSON_THROW_ON_ERROR), $output];
}

correction('real PHPUnit positive replay passes', static function (): void {
    [$status, $result, $output] = fixtureReplay('$this->assertTrue(true);');
    check($status === 0 && $result['pass'] && $result['tests'] === 1 && $result['assertions'] === 1, $output);
});

foreach (['markTestSkipped', 'markTestIncomplete'] as $method) {
    correction('real PHPUnit ' . $method . ' fails replay', static function () use ($method): void {
        [$status, $result, $output] = fixtureReplay('$this->' . $method . '("synthetic correction witness");');
        check($result['tests'] === 1 && $result['skipped'] === 1, 'Actual skipped/incomplete counter missing: ' . $output);
        check($status === 1 && $result['pass'] === false, 'Skipped/incomplete replay passed: ' . $output);
    });
}

correction('real PHPUnit xml.dist replay passes', static function (): void {
    [$status, $result, $output] = fixtureReplay('$this->assertTrue(true);', 'phpunit.xml.dist');
    check($status === 0 && $result['pass'], $output);
});

correction('discovery scans package roots, not wp/tests fixtures', static function (): void {
    check(function_exists('discoverT01Packages'), 'Shared custom package discovery is missing');
    $root = '/tmp/t01-discovery-' . bin2hex(random_bytes(6));
    foreach (['plugins/same', 'mu-plugins/same', 'themes/same', 'tests/fixture'] as $relative) {
        mkdir($root . '/' . $relative, 0777, true);
        file_put_contents($root . '/' . $relative . '/phpunit.xml.dist', '<phpunit/>');
    }
    mkdir($root . '/plugins/without-tests', 0777, true);
    file_put_contents($root . '/mu-plugins/standalone.php', '<?php');
    $discovery = discoverT01Packages($root);
    check(array_column($discovery['packages'], 'relative') === ['mu-plugins/same', 'plugins/same', 'themes/same'], 'Wrong discovered package inventory');
    check(array_column($discovery['packages'], 'cacheKey') === ['mu-plugins--same', 'same', 'themes--same'], 'Cache topology is not collision-safe/compatible');
    check(array_column($discovery['packages'], 'config') === ['phpunit.xml.dist', 'phpunit.xml.dist', 'phpunit.xml.dist'], 'Dist configs missing');
    check(array_column($discovery['warnings'], 'relative') === ['mu-plugins/standalone.php', 'plugins/without-tests'], 'Untested custom packages were not warned');
});

correction('repository discovery preserves historical caches and covers current roots', static function (): void {
    check(function_exists('discoverT01Packages'), 'Shared custom package discovery is missing');
    $discovery = discoverT01Packages('/repo/wp');
    $expected = [];
    $warnings = [];
    foreach (['plugins', 'mu-plugins', 'themes'] as $kind) {
        foreach (glob('/repo/wp/' . $kind . '/*', GLOB_ONLYDIR) ?: [] as $package) {
            $name = basename($package);
            if (is_file($package . '/phpunit.xml') || is_file($package . '/phpunit.xml.dist')) {
                $expected[$kind . '/' . $name] = $kind === 'plugins' ? $name : $kind . '--' . $name;
            } else {
                $warnings[] = $kind . '/' . $name;
            }
        }
        if ($kind === 'mu-plugins') {
            foreach (glob('/repo/wp/mu-plugins/*.php') ?: [] as $file) {
                $warnings[] = 'mu-plugins/' . basename($file);
            }
        }
    }
    ksort($expected);
    sort($warnings);
    check(array_column($discovery['packages'], 'relative') === array_keys($expected), 'Current repository package inventory incomplete');
    check(array_column($discovery['packages'], 'cacheKey') === array_values($expected), 'Existing prepared cache topology changed');
    check(array_column($discovery['warnings'], 'relative') === $warnings, 'Current untested custom packages are not warned');
});

foreach (['mu-plugins', 'themes'] as $kind) {
    correction('real replay discovers ' . $kind . ' config and correct prepared cache', static function () use ($kind): void {
        [$status, $result, $output] = fixtureReplay('$this->assertTrue(true);', 'phpunit.xml.dist', $kind);
        check($status === 0 && $result['pass'] && $result['tests'] === 1, $output);
        check(str_contains($output, '/work/' . $kind . '/imagine-pilotage/phpunit.xml.dist'), 'Disposable package topology changed: ' . $output);
    });
}

correction('real replay warns untested custom packages', static function (): void {
    [$status, $result, $output] = fixtureReplay('$this->assertTrue(true);');
    check($status === 0 && $result['pass'], $output);
    check(str_contains($output, 'T01 WARNING : plugins/untested'), 'Untested custom package was silently ignored: ' . $output);
});

correction('explicit full suffix is accepted', static function (): void {
    verifyCoverage(packageFixture('<directory suffix="Test.php">tests</directory>'));
});

correction('complete explicit file list is accepted', static function (): void {
    verifyCoverage(packageFixture('<file>tests/AlphaTest.php</file><file>tests/nested/BetaTest.php</file>'));
});

correction('standard schema declaration is accepted', static function (): void {
    verifyCoverage(packageFixture('<directory>tests</directory>', 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://schema.phpunit.de/11.5/phpunit.xsd"'));
});

foreach ([
    'missing test file' => '<file>tests/AlphaTest.php</file>',
    'duplicate file' => '<directory>tests</directory><file>tests/AlphaTest.php</file>',
    'empty selection' => '',
] as $name => $selection) {
    correction('refuses ' . $name, static function () use ($selection): void {
        rejected(static fn () => verifyCoverage(packageFixture($selection)), 'Non-exhaustive selection accepted');
    });
}

correction('real replay with exclude fails before PHPUnit', static function (): void {
    [$status, $result, $output] = fixtureReplay('$this->assertTrue(true);', 'phpunit.xml', 'plugins', '<directory>tests</directory><exclude>tests/SyntheticTest.php</exclude>');
    check($status === 1 && !$result['pass'] && $result['errors'] === 1 && $result['tests'] === 0, $output);
    check(str_contains($output, 'Unsupported PHPUnit selection element: exclude') && !str_contains($output, 'T01 COMMAND'), $output);
});

correction('configured package without Composer is refused, not silently omitted', static function (): void {
    [$status, $result, $output] = fixtureReplay('$this->assertTrue(true);', 'phpunit.xml', 'themes', '<directory>tests</directory>', false);
    check($status === 1 && !$result['pass'] && str_contains($output, 'requires themes/imagine-pilotage/composer.json'), $output);
});

correction('discovery refuses symbolic custom packages', static function (): void {
    $root = '/tmp/t01-symlink-' . bin2hex(random_bytes(6));
    mkdir($root . '/plugins', 0777, true);
    symlink('/opt/t01/imagine-pilotage', $root . '/plugins/linked');
    rejected(static fn () => discoverT01Packages($root), 'Symbolic custom package accepted');
});

correction('discovery refuses conflicting prepared cache keys', static function (): void {
    $root = '/tmp/t01-collision-' . bin2hex(random_bytes(6));
    foreach (['plugins/themes--same', 'themes/same'] as $relative) {
        mkdir($root . '/' . $relative, 0777, true);
        file_put_contents($root . '/' . $relative . '/phpunit.xml', '<phpunit/>');
    }
    rejected(static fn () => discoverT01Packages($root), 'Conflicting prepared cache keys accepted');
});

echo "T01 CORRECTIONS : $tests tests, $failures failures\n";
exit($failures === 0 ? 0 : 1);
