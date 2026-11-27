<?php

declare(strict_types=1);

use Imagine\OfflineDryRun\Analysis;

require '/subject/a30/Analysis.php';
$checks = [];
function check(string $name, bool $ok): void
{
    global $checks;
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
}
$rows = [];
foreach (range(2, 6) as $line) {
    $rows[] = ['line' => $line, 'rejected' => $line === 6,
        'email' => $line === 4 ? '' : 'fictif-' . $line . '@example.org',
        'product' => $line === 5 ? null : 910001, 'payment' => 'virement'];
}
$d = Analysis::analyse($rows, [910001 => true], [2 => 0, 3 => 1], false, 'classic');
check('five_closed_issues_exact_lines', array_column($d['rows'], 'issue', 'line') === [
    2 => 'compte_a_creer', 3 => 'compte_existant', 4 => 'sans_email',
    5 => 'type_a_decider', 6 => 'refuse_a13']);
check('no_row_values', !str_contains(json_encode($d), '@') && !str_contains(json_encode($d), 'fictif'));
$n = Analysis::analyse($rows, [910001 => true], [], true, 'hpos');
check('neutralised_no_guessed_matching', $n['neutralised'] && $n['rows'][0]['issue'] === null
    && $n['rows'][1]['issue'] === null && $n['rows'][2]['issue'] === 'sans_email');
$missing = Analysis::analyse($rows, [], [], false, 'classic');
check('missing_native_product_type_to_decide', $missing['rows'][0]['issue'] === 'type_a_decider');
try {
    Analysis::analyse($rows, [910001 => true], [2 => 2, 3 => 1], false, 'classic');
    check('duplicate_existing_refused_not_resolved', false);
} catch (RuntimeException $error) {
    check('duplicate_existing_refused_not_resolved', $error->getMessage() === 'A30_EXISTING_EMAIL_AMBIGUOUS');
}
check('reject_precedes_email_and_mapping', $missing['rows'][4]['issue'] === 'refuse_a13');
check('no_email_precedes_mapping', $missing['rows'][2]['issue'] === 'sans_email');
if (getenv('A30_PURE') === '1') {
    foreach ($checks as $row) {
        if ($row['status'] !== 'PASS') {
            exit(1);
        }
    }
    echo 'A30_PURE_OK ' . count($checks) . "\n";
    exit(0);
}
file_put_contents('/report/unit.json', json_encode(['checks' => $checks], JSON_PRETTY_PRINT) . "\n");
exit(count(array_filter($checks, static fn(array $row): bool => $row['status'] !== 'PASS')) > 0 ? 1 : 0);
