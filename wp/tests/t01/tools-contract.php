<?php

declare(strict_types=1);

define('T01_FUNCTIONS_ONLY', true);
require __DIR__ . '/executer.php';

// T02 contracts run only inside the unchanged disposable T01 boundary.
$tests = 0;
$failures = 0;
function toolContract(string $name, callable $body): void
{
    global $tests, $failures;
    $tests++;
    try {
        $body();
        echo "PASS $name\n";
    } catch (Throwable $error) {
        $failures++;
        echo "FAIL $name : " . $error->getMessage() . "\n";
    }
}
function toolExpect(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}
function toolFixture(): string
{
    $root = '/tmp/t02-contract-' . bin2hex(random_bytes(6));
    mkdir($root . '/tests/a90', 0777, true);
    mkdir($root . '/outils/bascule/a90', 0777, true);
    file_put_contents($root . '/tests/a90/unit.php', '<?php file_put_contents("/report/unit.json", json_encode(["checks" => [["check" => "synthetic", "status" => "PASS"]]]));');
    return $root;
}

toolContract('pure unit discovery is automatic and sorted', static function (): void {
    toolExpect(is_file(__DIR__ . '/tools.php'), 'T02 pure tool adapter missing');
    require_once __DIR__ . '/tools.php';
    $root = toolFixture();
    mkdir($root . '/tests/a89', 0777, true);
    file_put_contents($root . '/tests/a89/unit.php', '<?php');
    $found = discoverT01Tools($root);
    toolExpect(array_column($found['tools'], 'lot') === ['a89', 'a90'], 'Units were not discovered exactly once');
    toolExpect($found['excluded'] === [], 'Pure tools silently excluded');
});

if (is_file(__DIR__ . '/tools.php')) {
    require_once __DIR__ . '/tools.php';
}

toolContract('native unit is listed with its explicit reason, not executed', static function (): void {
    $root = toolFixture();
    file_put_contents($root . '/tests/a90/unit.hors-rejeu', "WordPress et base requis\n");
    $found = discoverT01Tools($root);
    toolExpect($found['tools'] === [] && $found['excluded'] === [
        ['lot' => 'a90', 'reason' => 'WordPress et base requis'],
    ], 'Native exclusion reason missing');
});

toolContract('real pure unit runs and its controls are counted', static function (): void {
    toolExpect(function_exists('runT01Tools'), 'T02 pure unit execution missing');
    $root = toolFixture();
    $before = hash_file('sha256', $root . '/tests/a90/unit.php');
    $result = runT01Tools($root, '/tmp/t02-run-' . bin2hex(random_bytes(6)));
    toolExpect($result['tools'] === 1 && $result['checks'] === 1 && $result['failures'] === 0, 'Real unit did not pass');
    toolExpect($before === hash_file('sha256', $root . '/tests/a90/unit.php'), 'Original unit changed');
});

toolContract('legacy boolean tests receipt is counted without changing the bank', static function (): void {
    $root = toolFixture();
    file_put_contents($root . '/tests/a90/unit.php', '<?php file_put_contents("/report/unit.json", json_encode(["tests" => ["first" => true, "second" => true], "exit_code" => 0]));');
    $result = runT01Tools($root, '/tmp/t02-run-' . bin2hex(random_bytes(6)));
    toolExpect($result['checks'] === 2 && $result['failures'] === 0, 'Legacy boolean bank omitted');
});

function toolReplayFixture(string $unit): array
{
    $root = toolFixture();
    $package = $root . '/plugins/imagine-pilotage';
    mkdir($package . '/tests', 0777, true);
    mkdir($root . '/cache', 0777, true);
    symlink('/opt/t01/imagine-pilotage', $root . '/cache/imagine-pilotage');
    foreach (['composer.json', 'composer.lock'] as $file) {
        copy('/opt/t01/imagine-pilotage/' . $file, $package . '/' . $file);
    }
    file_put_contents($package . '/phpunit.xml', '<phpunit bootstrap="vendor/autoload.php"><testsuites><testsuite name="Synthetic"><directory>tests</directory></testsuite></testsuites></phpunit>');
    file_put_contents($package . '/tests/KeepTest.php', '<?php final class KeepTest extends \\PHPUnit\\Framework\\TestCase { public function testKeep(): void { self::assertTrue(true); } }');
    file_put_contents($root . '/tests/a90/unit.php', $unit);
    foreach (['discovery.php', 'tools.php'] as $file) {
        copy(__DIR__ . '/' . $file, $root . '/' . $file);
    }
    file_put_contents($root . '/executer.php', str_replace(
        ['/repo/wp', '/tmp/t01/', '/opt/t01/', '/tmp/t01-tools'],
        [$root, $root . '/work/', $root . '/cache/', $root . '/tool-work'],
        file_get_contents(__DIR__ . '/executer.php')
    ));
    $process = proc_open(['php', $root . '/executer.php'], [
        0 => ['file', '/dev/null', 'r'], 1 => ['file', $root . '/stdout', 'w'], 2 => ['file', $root . '/stderr', 'w'],
    ], $pipes);
    toolExpect(is_resource($process), 'Replay not launched');
    $code = proc_close($process);
    $output = file_get_contents($root . '/stdout') . file_get_contents($root . '/stderr');
    toolExpect(preg_match('/^T01_RESULT (.+)$/m', $output, $matches) === 1, $output);
    return [$code, json_decode($matches[1], true, 512, JSON_THROW_ON_ERROR), $output];
}

toolContract('real failing tool vetoes real PHPUnit success without changing its totals', static function (): void {
    [$code, $result, $output] = toolReplayFixture('<?php file_put_contents("/report/unit.json", json_encode(["checks" => [["check" => "red", "status" => "FAIL"]]])); exit(1);');
    toolExpect($code === 1 && $result['pass'] === false && ($result['tools']['failures'] ?? 0) === 1, $output);
    toolExpect($result['tests'] === 1 && $result['assertions'] === 1 && $result['failures'] === 0, 'PHPUnit totals changed');
});

toolContract('a dangling symbolic unit is refused instead of silently omitted', static function (): void {
    $root = toolFixture();
    unlink($root . '/tests/a90/unit.php');
    symlink('/tmp/t02-absent-unit', $root . '/tests/a90/unit.php');
    $refused = false;
    try {
        discoverT01Tools($root);
    } catch (RuntimeException $error) {
        $refused = $error->getMessage() === 'T02_UNIT_SYMLINK';
    }
    toolExpect($refused, 'Dangling unit silently skipped');
});

toolContract('a nonzero receipt exit cannot be hidden by a zero process exit', static function (): void {
    $root = toolFixture();
    file_put_contents($root . '/tests/a90/unit.php', '<?php file_put_contents("/report/unit.json", json_encode(["checks" => [["check" => "green", "status" => "PASS"]], "exit_code" => 1]));');
    $result = runT01Tools($root, '/tmp/t02-run-' . bin2hex(random_bytes(6)));
    toolExpect($result['failures'] > 0, 'Receipt error ignored');
});

echo "T02 CONTRACT : $tests tests, $failures failures\n";
exit($failures === 0 ? 0 : 1);
