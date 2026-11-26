<?php

declare(strict_types=1);

require '/subject/a27/Analysis.php';

use Imagine\SavedPayments\Analysis;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
    if (!$ok) {
        throw new RuntimeException($name);
    }
};
$token = static fn(int $id = 1, int $user = 1, string $gateway = 'stripe', string $type = 'CC'): array => [
    'id' => $id, 'user' => $user, 'gateway' => $gateway, 'type' => $type, 'value' => 'A27_TOKEN_' . $id,
    'readable' => true, 'account' => true, 'year' => '2027', 'month' => '03'];
$sub = static fn(int $user = 1, string $gateway = 'stripe', array $ids = [1], array $meta = []): array => [
    'user' => $user, 'status' => 'active', 'manual' => false, 'gateway' => $gateway, 'tokens' => $ids,
    'metadata' => $meta, 'reference' => 'unknown'];
$date = '2026-11-26T12:00:00+00:00';
try {
    $check('cc_native_type', Analysis::tokenType('CC', 'stripe') === 'carte');
    $check('sepa_native_type', Analysis::tokenType('SEPA', 'stripe_sepa') === 'mandat_sepa');
    $check('echeck_not_automatically_sepa', Analysis::tokenType('eCheck', 'autre') === 'autre');
    $check('echeck_stripe_sepa', Analysis::tokenType('eCheck', 'stripe_sepa') === 'mandat_sepa');
    $check('unknown_native_type_not_absent', Analysis::tokenType('', 'stripe') === 'illisible');
    $check('arbitrary_native_type_closed', Analysis::tokenType('A27_PRIVATE_CANARY', 'stripe') === 'autre');
    $check('gateway_canary_closed', Analysis::gateway('a27_private_canary') === 'autre');
    $check('gateway_empty_closed', Analysis::gateway('') === 'aucune');
    $check('past_card', Analysis::expiry('2026', '10', $date) === 'expired');
    $check('current_month_not_expired', Analysis::expiry('2026', '11', $date) === 'within_six_months');
    $check('fifth_month', Analysis::expiry('2027', '04', $date) === 'within_six_months');
    $check('sixth_month_end_after_exact_window', Analysis::expiry('2027', '05', $date) === 'later');
    $check('later_card', Analysis::expiry('2030', '01', $date) === 'later');
    $check('six_months_end_of_month_clamp',
        Analysis::expiry('2027', '02', '2026-08-31T23:59:59+00:00') === 'within_six_months');
    $check('utc_end_second_valid', Analysis::expiry('2026', '11', '2026-11-30T23:59:59+00:00') !== 'expired');
    $check('utc_next_second_expired', Analysis::expiry('2026', '11', '2026-12-01T00:00:00+00:00') === 'expired');
    foreach ([['', ''], ['2027', '13'], ['A27_PRIVATE_CANARY', '01'], ['2027', '1']] as $i => [$year, $month]) {
        $check('expiry_unreadable_' . $i, Analysis::expiry($year, $month, $date) === 'illisible');
    }
    foreach (['2026-02-30T12:00:00+00:00', '2026-11-26T12:00:00Z', 'A27_PRIVATE_CANARY'] as $i => $clock) {
        $refused = false;
        try {
            Analysis::clock($clock);
        } catch (RuntimeException $e) {
            $refused = $e->getMessage() === 'A27_CLOCK_INVALID';
        }
        $check('clock_closed_' . $i, $refused);
    }
    $t = $token();
    $s = $sub();
    $r = Analysis::reference($s, [$t]);
    $check('own_linked_card', $r['type'] === 'carte' && $r['link'] === 'linked' && $r['present']);
    $r = Analysis::reference($sub(2), [$t]);
    $check('foreign_account_not_linked', $r['type'] === 'illisible' && $r['link'] === 'unlinked');
    $r = Analysis::reference($sub(1, 'paypal'), [$t]);
    $check('foreign_gateway_not_linked', $r['type'] === 'illisible' && $r['link'] === 'unlinked');
    $r = Analysis::reference($sub(0), [$t]);
    $check('guest_not_linked', $r['link'] === 'unlinked');
    $r = Analysis::reference($sub(1, 'stripe', [], ['_stripe_source_id' => 'A27_TOKEN_1']), [$t]);
    $check('native_metadata_matched_without_order_token_id', $r['type'] === 'carte' && $r['link'] === 'linked');
    $r = Analysis::reference($sub(1, 'stripe', [], ['_stripe_source_id' => 'A27_UNMATCHED_CANARY']), [$t]);
    $check('unmatched_stripe_type_unreadable_not_invented_card',
        $r['type'] === 'illisible' && $r['link'] === 'unlinked');
    $r = Analysis::reference($sub(1, 'paypal', [], ['_paypal_subscription_id' => 'A27_AGREEMENT_CANARY']), []);
    $check('paypal_native_reference_without_token', $r['type'] === 'accord_paypal' && $r['link'] === 'unlinked');
    $r = Analysis::reference($sub(1, 'stripe_sepa', [], ['_stripe_source_id' => 'A27_MANDATE_CANARY']), []);
    $check('sepa_native_source_without_token', $r['type'] === 'mandat_sepa' && $r['link'] === 'unlinked');
    $r = Analysis::reference($sub(1, 'stripe', [1, 2]), [$t, $token(2)]);
    $check('multiple_no_default_guessed', $r['type'] === 'illisible' && $r['link'] === 'unknown');
    $r = Analysis::reference($sub(1, 'stripe', [], ['x' => ['A27_CANARY']]), [$t]);
    $check('non_scalar_metadata_unreadable', $r['type'] === 'illisible' && $r['link'] === 'unknown');
    $r = Analysis::reference($sub(1, 'stripe', [], ['x' => 'one', 'y' => 'two']), [$t]);
    $check('conflicting_metadata_unreadable', $r['type'] === 'illisible');
    $bad = $t;
    $bad['readable'] = false;
    $check('unloadable_token_not_absent', Analysis::reference($s, [$bad])['type'] === 'illisible');
    $bad = $s;
    $bad['tokens'] = [];
    $bad['reference'] = 'absent';
    $check('known_absent_not_saved_reference', Analysis::reference($bad, [])['present'] === false);
    $rows = array_fill(0, 5, $s);
    $a = Analysis::analyse($rows, [$t], $date, false);
    $check('exact_five_visible', $a['automatic'] === ['groups' => [
        ['gateway' => 'stripe', 'type' => 'carte', 'count' => 5]], 'autres' => 0]);
    $check('exact_five_cards_window', $a['cards'] === ['groups' => [
        ['gateway' => 'stripe', 'expiry' => 'within_six_months', 'count' => 5]], 'autres' => 0]);
    $a = Analysis::analyse(array_slice($rows, 0, 4), [$t], $date, false);
    $check('four_pooled', $a['automatic'] === ['groups' => [], 'autres' => 4]);
    foreach (Analysis::LIVE as $state) {
        $s['status'] = $state;
        $check('live_state_' . $state, Analysis::analyse([$s], [$t], $date, false)['automatic']['autres'] === 1);
    }
    foreach (['expired', 'cancelled', 'trash', 'draft'] as $state) {
        $s['status'] = $state;
        $check('not_live_' . $state, Analysis::analyse([$s], [$t], $date, false)['automatic']['autres'] === 0);
    }
    $s = $sub();
    $s['manual'] = true;
    $check('manual_excluded_from_automatic', Analysis::analyse([$s], [$t], $date, false)['automatic']['autres'] === 0);
    $a = Analysis::analyse([], [$t, $token(2)], $date, false);
    $check('orphan_tokens_and_multi_account_not_subscriptions', $a['relations']['autres'] === 3);
    $a = Analysis::analyse([$sub()], [$t, $token(2)], $date, false);
    $check('unattached_token_on_living_account_not_orphan', $a['relations']['autres'] === 1);
    $unknown = $t;
    $unknown['account'] = false;
    $a = Analysis::analyse([], [$unknown], $date, false);
    $check('missing_account_is_unknown_not_orphan', $a['relations']['autres'] === 1);
    $n = Analysis::analyse([$sub()], [$t], $date, true);
    $check('all_neutralised_unknown_never_zero',
        $n === array_fill_keys(['automatic', 'cards', 'relations'], Analysis::UNKNOWN));
    $check('no_private_values', !str_contains(json_encode([$a, $n]), 'CANARY'));
} catch (Throwable $error) {
    $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'detail' => get_class($error)];
}
$result = ['suite' => 'A27-pure', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
if (getenv('A27_PURE_INCLUDE') !== '1') {
    file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
    echo 'A27_UNIT ' . count($checks) . "\n";
    exit($result['exit_code']);
}
