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

echo "T02 CONTRACT : $tests tests, $failures failures\n";
exit($failures === 0 ? 0 : 1);
