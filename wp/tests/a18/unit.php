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
$check('national_11_digits_not_a_card', Forms::national('85073003328') && !Forms::card('85073003328'));
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
]) === [['scope' => 'order', 'store' => 'commun', 'key' => 'autre', 'iban' => 1, 'card' => 0, 'national' => 0]]);
foreach ([
    'multiple_spaces' => '  ',
    'line_feed' => "\n",
    'tabs' => "\t\t",
    'crlf' => "\r\n",
    'nbsp' => "\u{00a0}\u{00a0}",
    'narrow_nbsp' => "\u{202f}\u{202f}",
] as $label => $separator) {
    $iban = implode($separator, ['BE68', '5390', '0754', '7034']);
    $card = implode($separator, ['4242', '4242', '4242', '4242']);
    $check('r3_iban_scan_to_groups_' . $label, Forms::iban($iban)
        && Forms::scan($iban)['iban'] === true
        && Imagine\RetentionInventory\Inventory::groups([
            ['scope' => 'option', 'key' => '_r3_iban', 'value' => $iban . ';' . $iban],
        ]) === [['scope' => 'option', 'store' => 'commun', 'key' => '_r3_iban',
            'iban' => 1, 'card' => 0, 'national' => 0]]);
    $check('r3_card_scan_to_groups_' . $label, Forms::card($card)
        && Forms::scan($card)['card'] === true
        && Imagine\RetentionInventory\Inventory::groups([
            ['scope' => 'account', 'key' => '_r3_card', 'value' => $card . ';' . $card],
        ]) === [['scope' => 'account', 'store' => 'commun', 'key' => '_r3_card',
            'iban' => 0, 'card' => 1, 'national' => 0]]);
}
foreach ([
    'card_trailing_digits' => ['4242 4242 4242 4242 123', 'card'],
    'card_leading_digits' => ['123 4242 4242 4242 4242', 'card'],
    'card_both_sides' => ['987 4242 4242 4242 4242 123', 'card'],
    'register_trailing_year' => ['85.07.30-033.28 2026', 'national'],
    'register_leading_year' => ['2026 85.07.30-033.28', 'national'],
    'register_both_sides' => ['2026 85.07.30-033.28 2027', 'national'],
] as $label => [$text, $form]) {
    $flags = Forms::scan($text);
    $groups = Imagine\RetentionInventory\Inventory::groups([
        ['scope' => 'account', 'key' => '_r2', 'value' => $text . ';' . $text],
    ]);
    $check('r2_' . $label, $flags[$form] && count($groups) === 1 && $groups[0][$form] === 1);
}
foreach ([
    'card_contiguous_suffix' => ['424242424242424212345678901', 'card'],
    'card_contiguous_prefix' => ['1234567894242424242424242', 'card'],
    'register_contiguous_suffix' => ['850730033282026', 'national'],
    'register_contiguous_prefix' => ['202685073003328', 'national'],
    'card_attached_letters' => ['x4242424242424242y', 'card'],
    'register_attached_letters' => ['x85073003328y', 'national'],
] as $label => [$text, $form]) {
    $check('r2_no_arbitrary_fragment_' . $label, !Forms::scan($text)[$form]);
}
// The JSON is really loaded once, then made unavailable in a disposable class copy.
mkdir('/report/memo');
file_put_contents('/report/memo/Forms.php', str_replace(
    'namespace Imagine\\RetentionInventory;',
    'namespace Imagine\\RetentionMemoProbe;',
    file_get_contents('/subject/a18/Forms.php')
));
copy('/subject/a18/iban-structures.json', '/report/memo/iban-structures.json');
require '/report/memo/Forms.php';
$memoFirst = Imagine\RetentionMemoProbe\Forms::iban('BE68539007547034');
file_put_contents('/report/memo/iban-structures.json', '{}');
$check('memo_iban_registry_single_load', $memoFirst
    && Imagine\RetentionMemoProbe\Forms::iban('BE68539007547034')
    && Imagine\RetentionMemoProbe\Forms::scan('BE68 5390 0754 7034')['iban']);
unlink('/report/memo/Forms.php');
unlink('/report/memo/iban-structures.json');
rmdir('/report/memo');
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
