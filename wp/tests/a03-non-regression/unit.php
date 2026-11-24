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
test('page_health_and_date_movement_are_anomalous', function (): void {
    $a = ['schema' => 'imagine-a03-v1', 'generated_at_utc' => 'old', 'pages' => ['home' => ['status' => 200, 'marker' => true, 'php_error' => false]], 'subscriptions' => [9 => ['next_payment_utc' => '2027-01-01 00:00:00']]];
    $b = $a;
    $b['generated_at_utc'] = 'new';
    expect(Imagine\NonRegression\Report::compare($a, $b)['changes'] === []);
    $b['pages']['home']['marker'] = false;
    $b['subscriptions'][9]['next_payment_utc'] = '2027-01-02 00:00:00';
    expect(Imagine\NonRegression\Report::compare($a, $b)['anormal'] === 2);
    $b = $a;
    $b['pages']['home']['status'] = 302;
    expect(Imagine\NonRegression\Report::compare($a, $b)['changes'][0]['class'] === 'a regarder');
});
test('database_host_is_literal_and_bounded', function (): void {
    expect(Imagine\NonRegression\Policy::dsn(['DB_HOST' => 'localhost:/scratch/mysql.sock', 'DB_NAME' => 'a03']) === 'mysql:unix_socket=/scratch/mysql.sock;dbname=a03;charset=utf8mb4');
    expect(Imagine\NonRegression\Policy::dsn(['DB_HOST' => 'db:3306', 'DB_NAME' => 'a03']) === 'mysql:host=db;port=3306;dbname=a03;charset=utf8mb4');
    try {
        Imagine\NonRegression\Policy::dsn(['DB_HOST' => 'db;host=other', 'DB_NAME' => 'a03']);
        expect(false);
    } catch (RuntimeException $error) {
        expect($error->getMessage() === 'A03_DB_HOST');
    }
});
file_put_contents('/report/unit.json', json_encode(['tests' => $checks, 'exit_code' => (int) in_array(false, $checks, true)], JSON_PRETTY_PRINT) . "\n");
exit((int) in_array(false, $checks, true));
