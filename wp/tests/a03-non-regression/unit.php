<?php

declare(strict_types=1);

$checks = [];
function test(string $name, callable $body): void
{
    global $checks;
    try {
        $body();
        $checks[$name] = true;
    } catch (Throwable $error) {
        $checks[$name] = false;
        echo $name . ': ' . $error->getMessage() . "\n";
    }
}
function expect(bool $ok): void
{
    if (!$ok) {
        throw new RuntimeException('assertion failed');
    }
}
define('IMAGINE_A03_LIBRARY_ONLY', true);
$subject = '/subject/non-regression';
if (is_file($subject)) {
    require $subject;
}
test('comparison_classifies_versions_access_and_scheduler', function (): void {
    $a = ['schema' => 'imagine-a03-v1', 'versions' => ['wordpress' => '6.8.3'], 'access' => ['10:20' => true], 'actions' => ['1' => ['hook' => 'example', 'date' => '2026-12-01 00:00:00']]];
    expect(Imagine\NonRegression\Report::compare($a, $a)['changes'] === []);
    $b = $a;
    $b['versions']['wordpress'] = '6.9.1';
    $b['access']['10:20'] = false;
    unset($b['actions']['1']);
    $diff = Imagine\NonRegression\Report::compare($a, $b);
    expect(array_column($diff['changes'], 'class') === ['attendu', 'anormal', 'anormal']);
    expect($diff['anormal'] === 2);
});
test('verified_marker_and_explicit_write_gate', function (): void {
    $marker = ['status' => 'verified', 'offline_verified' => true, 'runtime_probe_passed' => true];
    expect(Imagine\NonRegression\Policy::verified($marker));
    $marker['runtime_probe_passed'] = false;
    expect(!Imagine\NonRegression\Policy::verified($marker));
    expect(!Imagine\NonRegression\Policy::renewalAllowed(false, true, true));
    expect(!Imagine\NonRegression\Policy::renewalAllowed(true, false, true));
    expect(!Imagine\NonRegression\Policy::renewalAllowed(true, true, false));
    expect(Imagine\NonRegression\Policy::renewalAllowed(true, true, true));
});
file_put_contents('/report/unit.json', json_encode(['tests' => $checks, 'exit_code' => (int) in_array(false, $checks, true)], JSON_PRETTY_PRINT) . "\n");
exit((int) in_array(false, $checks, true));
