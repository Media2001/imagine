<?php

declare(strict_types=1);

require '/subject/a18/Forms.php';

use Imagine\RetentionInventory\Forms;

$checks = [];
function check(string $name, bool $ok): void
{
    global $checks;
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
}
check('iban_valid_invalid_structure_and_checksum', Forms::iban('BE68539007547034')
    && !Forms::iban('BE69539007547034') && !Forms::iban('BE68ABCD07547034'));
check('card_luhn_and_length', method_exists(Forms::class, 'card')
    && Forms::card('4242 4242 4242 4242') && !Forms::card('4242424242424243')
    && !Forms::card('0000000000000000') && !Forms::card('42424242'));
check('belgian_register_both_centuries_checksum_only', method_exists(Forms::class, 'national')
    && Forms::national('85.07.30-033.28') && Forms::national('00.01.01-001.05')
    && !Forms::national('85073003329'));
check('embedded_serialized_counted_once_per_form', method_exists(Forms::class, 'scan')
    && Forms::scan('a:2:{s:4:"iban";s:16:"BE68539007547034";s:5:"again";s:16:"BE68539007547034";}')
    === ['iban' => true, 'card' => false, 'national' => false]);
check('embedded_card_and_canary_not_returned', method_exists(Forms::class, 'scan')
    && Forms::scan('PRIVATE_CANARY card=4242424242424242; end')
    === ['iban' => false, 'card' => true, 'national' => false]);
$result = ['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
exit($result['exit_code']);
