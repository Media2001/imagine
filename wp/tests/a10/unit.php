<?php

declare(strict_types=1);

$checks = [];
function a10_check(string $name, bool $ok): void
{
    global $checks;
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
}
$file = '/subject/a10/Projection.php';
if (!is_file($file)) {
    a10_check('projection_module_exists', false);
} else {
    require $file;
    $p = Imagine\CouponInventory\Projection::class;
    a10_check('recurrence_standard_types', $p::recurring('recurring_fee') === true && $p::recurring('recurring_percent') === true && $p::recurring('percent') === false && $p::recurring('sign_up_fee_percent') === false && $p::recurring('custom') === null);
    a10_check('numeric_only', $p::number('42') === 42 && $p::number('private') === null && $p::decimal('2.50') === '2.50' && $p::decimal('canary') === null);
    a10_check('product_id_formats', $p::ids('12,34,0') === [12, 34] && $p::ids('a:2:{i:0;i:12;i:1;i:34;}') === [12, 34]);
    a10_check('email_count_only', $p::emailCount('a:2:{i:0;s:15:"one@example.org";i:1;s:15:"two@example.org";}') === 2 && $p::emailCount('one@example.org') === 1 && $p::emailCount('') === 0);
    a10_check('utc_expiry', $p::expiry('1795608000', new DateTimeZone('UTC')) === '2026-11-25T12:00:00Z' && $p::expiry('', new DateTimeZone('UTC')) === null);
    a10_check('calendar_window_clamped', $p::cutoff(new DateTimeImmutable('2024-02-29T12:00:00Z')) === '2023-02-28 12:00:00');
    a10_check('empty_amount_unknown', $p::decimal('') === null);
    foreach (['a:1:{i:0;a:0:{}}', 'a:broken', '12,invalid'] as $i => $invalid) {
        try {
            $p::ids($invalid);
            a10_check('invalid_structured_meta_' . $i, false);
        } catch (RuntimeException $error) {
            a10_check('invalid_structured_meta_' . $i, $error->getMessage() === 'A10_META_INVALID');
        }
    }
}
file_put_contents('/report/unit.json', json_encode(['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)], JSON_PRETTY_PRINT) . "\n");
foreach ($checks as $check) {
    echo $check['check'] . ':' . $check['status'] . "\n";
}
exit((int) in_array('FAIL', array_column($checks, 'status'), true));
