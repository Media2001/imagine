<?php

declare(strict_types=1);

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$available = is_file('/subject/a14/Matcher.php');
$check('matcher_exists', $available);
if ($available) {
    require '/subject/a14/Matcher.php';
    $result = \Imagine\Contacts\Matcher::build(
        [['line' => 2, 'email' => ' Alice @EXAMPLE.ORG ', 'status' => 'desinscrit']],
        [
            ['email' => 'alice@example.org', 'active' => true, 'technical' => false],
            ['email' => 'other@example.org', 'active' => false, 'technical' => false],
            ['email' => 'technical@example.org', 'active' => false, 'technical' => true],
        ]
    );
    $check('case_spaces_match_only', $result['counts']['contacts_with_account'] === 1);
    $check('unmatched_account_and_technical_excluded', $result['counts']['accounts_without_contact'] === 1);
    $check('status_and_unknown_fields_preserved', $result['matched'] === [
        ['line' => 2, 'active_subscription' => true, 'status' => 'desinscrit', 'cooperateur' => '', 'tarif' => ''],
    ]);
    $check('no_email_in_any_output', !str_contains(json_encode($result, JSON_THROW_ON_ERROR), '@'));
}
$exit = in_array('FAIL', array_column($checks, 'status'), true) ? 1 : 0;
file_put_contents('/report/unit.json', json_encode(['exit_code' => $exit, 'checks' => $checks], JSON_PRETTY_PRINT));
exit($exit);
