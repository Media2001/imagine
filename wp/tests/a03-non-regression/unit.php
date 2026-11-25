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
function a03Photo(): array
{
    $pages = [];
    foreach (['home', 'open', 'restricted', 'shop', 'cart', 'checkout', 'account'] as $page) {
        $pages[$page] = ['status' => 200, 'final_status' => 200, 'marker' => true, 'php_error' => false];
    }
    return [
        'schema' => 'imagine-a03-v1', 'generated_at_utc' => '2026-11-24T00:00:00+00:00',
        'versions' => ['wordpress' => '6.8.3', 'php' => '8.2.33', 'woocommerce' => '10.0',
            'memberships' => '1.0', 'subscriptions' => '1.0'],
        'storage' => 'classic',
        'sample_states' => ['membership' => ['none' => true], 'subscription' => ['none' => true]],
        'samples' => ['none:none' => 10], 'memberships' => [], 'access' => ['10:20' => true],
        'subscriptions' => [9 => ['status' => 'active', 'gateway' => 'manual', 'period' => 'month',
            'interval' => 1, 'next_payment_utc' => '2027-01-01 00:00:00']],
        'subscription_counts' => ['status' => ['active' => 1], 'gateway' => ['manual' => 1],
            'period' => ['1-month' => 1]],
        'actions' => [1 => ['hook' => 'example', 'date' => '2026-12-01 00:00:00']],
        'action_days' => ['example:2026-12-01' => 1],
        'order_months' => array_map(static fn(int $month): string => sprintf('2026-%02d', $month), range(1, 12)),
        'orders' => [], 'php_log' => ['checked' => true, 'from_utc' => '2026-11-24T00:00:00Z',
            'until_utc' => '2026-11-24T00:00:01Z', 'errors' => 0],
        'pages' => $pages, 'renewal' => ['enabled' => false],
    ];
}
function a03Probe(): array
{
    return ['schema' => 'imagine-a03-v1', 'mode' => 'renewal_probe', 'renewal' => [
        'enabled' => true, 'manual_only' => true, 'created' => true,
        'linked' => true, 'pending' => true, 'cleaned' => true,
    ]];
}
function a03Refused(array $before, array $after, string $code): void
{
    try {
        Imagine\NonRegression\Report::compare($before, $after);
        throw new RuntimeException('report unexpectedly accepted');
    } catch (RuntimeException $error) {
        expect($error->getMessage() === $code);
    }
}
define('IMAGINE_A03_LIBRARY_ONLY', true);
$subject = '/subject/non-regression';
if (is_file($subject)) {
    require $subject;
}
test('comparison_classifies_versions_access_and_scheduler', function (): void {
    $a = a03Photo();
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
    $a = a03Photo();
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
    expect(Imagine\NonRegression\Policy::dsn(['DB_HOST' => 'localhost:/scratch/mysql.sock', 'DB_NAME'
        => 'a03']) === 'mysql:unix_socket=/scratch/mysql.sock;dbname=a03;charset=utf8mb4');
    expect(Imagine\NonRegression\Policy::dsn(['DB_HOST' => 'db:3306', 'DB_NAME'
        => 'a03']) === 'mysql:host=db;port=3306;dbname=a03;charset=utf8mb4');
    try {
        Imagine\NonRegression\Policy::dsn(['DB_HOST' => 'db;host=other', 'DB_NAME' => 'a03']);
        expect(false);
    } catch (RuntimeException $error) {
        expect($error->getMessage() === 'A03_DB_HOST');
    }
});
test('incomplete_reports_are_refused', function (): void {
    a03Refused(['schema' => 'imagine-a03-v1'], ['schema' => 'imagine-a03-v1'], 'A03_REPORT_STRUCTURE');
    foreach (array_keys(a03Photo()) as $section) {
        if ($section === 'schema') {
            continue;
        }
        $bad = a03Photo();
        unset($bad[$section]);
        a03Refused($bad, $bad, 'A03_REPORT_STRUCTURE');
    }
});
test('renewal_modes_are_complete_and_not_interchangeable', function (): void {
    $probe = a03Probe();
    expect(Imagine\NonRegression\Report::compare($probe, $probe)['changes'] === []);
    a03Refused(a03Photo(), $probe, 'A03_REPORT_MODE');
    a03Refused($probe, a03Photo(), 'A03_REPORT_MODE');
    unset($probe['renewal']['cleaned']);
    a03Refused($probe, $probe, 'A03_REPORT_STRUCTURE');
});
test('disappearing_page_is_anomalous', function (): void {
    $before = a03Photo();
    $after = $before;
    unset($after['pages']['home']);
    expect(Imagine\NonRegression\Report::compare($before, $after)['changes'] === [
        ['path' => 'pages.home', 'class' => 'anormal'],
    ]);
});
test('section_keys_refuse_personal_names', function (): void {
    $bad = a03Photo();
    $bad['access']['Jean.Dupont'] = true;
    a03Refused($bad, $bad, 'A03_REPORT_STRUCTURE');
    $before = a03Photo();
    $before['samples']['jean-dupont:none'] = 10;
    $after = $before;
    $after['samples']['jean-dupont:none'] = 11;
    expect(!str_contains(json_encode(Imagine\NonRegression\Report::compare($before, $after)), 'jean-dupont'));
});
test('sample_state_dictionary_does_not_reindex', function (): void {
    $before = a03Photo();
    $before['sample_states']['membership']['active'] = true;
    $after = $before;
    unset($after['sample_states']['membership']['active']);
    expect(count(Imagine\NonRegression\Report::compare($before, $after)['changes']) === 1);
});
test('comparer_cli_rejects_malformed_reports_without_leaking_keys', function (): void {
    $badKey = a03Photo();
    $badKey['access']['Jean.Dupont'] = true;
    $lostPage = a03Photo();
    unset($lostPage['pages']['home']);
    foreach ([
        [['schema' => 'imagine-a03-v1'], ['schema' => 'imagine-a03-v1'], 1],
        [a03Photo(), a03Probe(), 1], [a03Probe(), a03Photo(), 1],
        [$badKey, $badKey, 1], [a03Photo(), $lostPage, 2],
    ] as $i => [$before, $after, $expected]) {
        $files = ['/report/compare-before-' . $i . '.json', '/report/compare-after-' . $i . '.json'];
        foreach ([$before, $after] as $index => $report) {
            file_put_contents($files[$index], json_encode($report, JSON_THROW_ON_ERROR));
        }
        $process = proc_open(['php', '/subject/comparer', ...$files], [
            0 => ['file', '/dev/null', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w'],
        ], $pipes);
        expect(is_resource($process));
        $stdout = stream_get_contents($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        expect(proc_close($process) === $expected);
        expect(!str_contains($stdout . $stderr, 'Jean'));
        if ($expected === 1) {
            expect($stdout === '' && $stderr === "A03_COMPARE_REFUSED\n");
        } else {
            expect(json_decode($stdout, true, 64, JSON_THROW_ON_ERROR)['changes'] === [
                ['path' => 'pages.home', 'class' => 'anormal'],
            ]);
        }
        foreach ($files as $file) {
            unlink($file);
        }
    }
});
file_put_contents('/report/unit.json', json_encode(['tests' => $checks, 'exit_code' => (int) in_array(
    false,
    $checks,
    true
)], JSON_PRETTY_PRINT) . "\n");
exit((int) in_array(false, $checks, true));
