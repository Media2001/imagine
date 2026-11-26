<?php

declare(strict_types=1);

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$available = is_file('/checkout/wp/outils/bascule/a14/Matcher.php');
$check('matcher_exists', $available);
if ($available) {
    require '/checkout/wp/outils/bascule/a14/Matcher.php';
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
    $more = \Imagine\Contacts\Matcher::build([
        ['line' => 2, 'email' => 'same@example.org', 'status' => 'inscrit'],
        ['line' => 3, 'email' => ' SAME @EXAMPLE.ORG ', 'status' => 'bloque'],
        ['line' => 4, 'email' => 'not-an-email', 'status' => 'inscrit'],
        ['line' => 5, 'email' => '', 'status' => 'inscrit'],
    ], []);
    $check('duplicates_all_members_and_invalid_lines', ($more['anomalies'] ?? null) === [
        ['line' => 2, 'reason' => 'Doublon dans le fichier'],
        ['line' => 3, 'reason' => 'Doublon dans le fichier'],
        ['line' => 4, 'reason' => 'Adresse électronique invalide'],
        ['line' => 5, 'reason' => 'Adresse électronique invalide'],
    ]);
    $check('invalid_not_counted_as_unmatched', $more['counts']['contacts_without_account'] === 2);
    $ambiguous = \Imagine\Contacts\Matcher::build(
        [['line' => 2, 'email' => 'shared@example.org', 'status' => 'inscrit']],
        [
            ['email' => 'shared@example.org', 'active' => true, 'technical' => false],
            ['email' => ' SHARED @example.org', 'active' => false, 'technical' => false],
        ]
    );
    $check('ambiguous_accounts_never_pick_first', $ambiguous['matched'] === []
        && ($ambiguous['counts']['ambiguous_contact_lines'] ?? 0) === 1);
}
$exit = in_array('FAIL', array_column($checks, 'status'), true) ? 1 : 0;
file_put_contents('/report/unit.json', json_encode(['exit_code' => $exit, 'checks' => $checks], JSON_PRETTY_PRINT));
exit($exit);
