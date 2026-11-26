<?php

declare(strict_types=1);

require '/subject/a18/Forms.php';
require '/subject/a18/Inventory.php';

use Imagine\RetentionInventory\Forms;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$check('iban_valid_invalid_structure_and_checksum', Forms::iban('BE68539007547034')
    && !Forms::iban('BE69539007547034') && !Forms::iban('BE68ABCD07547034'));
$check('card_luhn_and_length', method_exists(Forms::class, 'card')
    && Forms::card('4242 4242 4242 4242') && !Forms::card('4242424242424243')
    && !Forms::card('0000000000000000') && !Forms::card('42424242'));
$check('belgian_register_both_centuries_checksum_only', method_exists(Forms::class, 'national')
    && Forms::national('85.07.30-033.28') && Forms::national('00.01.01-001.05')
    && !Forms::national('85073003329'));
$check('embedded_serialized_counted_once_per_form', method_exists(Forms::class, 'scan')
    && Forms::scan('a:2:{s:4:"iban";s:16:"BE68539007547034";s:5:"again";s:16:"BE68539007547034";}')
    === ['iban' => true, 'card' => false, 'national' => false]);
$check('embedded_card_and_canary_not_returned', method_exists(Forms::class, 'scan')
    && Forms::scan('PRIVATE_CANARY card=4242424242424242; end')
    === ['iban' => false, 'card' => true, 'national' => false]);
try {
    $check('native_nullable_meta_not_fatal', Imagine\RetentionInventory\Inventory::groups([
        ['scope' => 'order', 'key' => '_nullable', 'value' => null],
    ]) === []);
} catch (Throwable) {
    $check('native_nullable_meta_not_fatal', false);
}
$check('binary_prefix_does_not_hide_payment_shape', Forms::scan("\xff;4242424242424242;")['card'] === true);
$check('non_belgian_iban_and_unicode_spaces', Forms::scan("GB82 WEST 1234 5698 7654 32")['iban']
    && Forms::iban("BE68\u{202f}5390\u{00a0}0754 7034")
    && !Forms::iban('ZZ68539007547034'));
$check('unsafe_key_masked_no_value_output', Imagine\RetentionInventory\Inventory::groups([
    ['scope' => 'order', 'key' => '/A18_PRIVATE_CANARY', 'value' => 'BE68539007547034'],
]) === [['scope' => 'order', 'key' => 'autre', 'iban' => 1, 'card' => 0, 'national' => 0]]);
mkdir('/report/unit-media');
mkdir('/report/unit-media/alpha');
mkdir('/report/unit-media/beta');
$dirs = [];
foreach (new DirectoryIterator('/report/unit-media') as $entry) {
    if (!$entry->isDot()) {
        $dirs[] = $entry->getPathname();
    }
}
file_put_contents($dirs[1] . '/probe.txt', 'XXX');
try {
    $media = Imagine\RetentionInventory\Inventory::media('/report/unit-media');
    $check('empty_unknown_before_nonempty_merges', count($media) === 1
        && $media[0]['directories'] === 2 && $media[0]['files'] === ['txt' => 1] && $media[0]['bytes'] === 3);
} catch (Throwable) {
    $check('empty_unknown_before_nonempty_merges', false);
}
unlink($dirs[1] . '/probe.txt');
rmdir($dirs[0]);
rmdir($dirs[1]);
rmdir('/report/unit-media');
$result = ['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
exit($result['exit_code']);
