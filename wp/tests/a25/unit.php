<?php

declare(strict_types=1);

require '/subject/a25/Analysis.php';

use Imagine\VisitorRetention\Analysis;

$checks = [];
function imagine_a25_check(string $name, bool $ok): void
{
    global $checks;
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
    if (!$ok) {
        throw new RuntimeException($name);
    }
}

try {
    $rows = [
        ['year' => 2023, 'state' => '1', 'email' => true, 'ip' => true, 'account' => false],
        ['year' => 2024, 'state' => '0', 'email' => false, 'ip' => false, 'account' => true],
        ['year' => 2024, 'state' => 'spam', 'email' => true, 'ip' => true, 'account' => false],
    ];
    $forms = [['year' => 2023, 'state' => 'Fluent Forms', 'count' => 2],
        ['year' => 2024, 'state' => 'autre', 'count' => 2]];
    $a = Analysis::analyse($rows, $forms, [2023, 2024], false);
    imagine_a25_check('three_comments_two_years_pooled', $a['comments']['all'] === ['groups' => [], 'autres' => 3]);
    imagine_a25_check('email_count_exact', $a['comments']['email'] === ['groups' => [], 'autres' => 2]);
    imagine_a25_check('ip_count_exact', $a['comments']['ip'] === ['groups' => [], 'autres' => 2]);
    imagine_a25_check('linked_count_exact', $a['comments']['account'] === ['groups' => [], 'autres' => 1]);
    imagine_a25_check('form_entries_exact_pooled', $a['forms'] === ['groups' => [], 'autres' => 4]);
    imagine_a25_check('guest_orders_exact_pooled', $a['guests'] === ['groups' => [], 'autres' => 2]);
    $n = Analysis::analyse($rows, $forms, [2023, 2024], true);
    imagine_a25_check('neutral_email_unknown_never_zero', $n['comments']['email'] === Analysis::UNKNOWN);
    imagine_a25_check('neutral_ip_unknown_never_zero', $n['comments']['ip'] === Analysis::UNKNOWN);
    imagine_a25_check('neutral_forms_conservative_unknown', $n['forms'] === Analysis::UNKNOWN);
    imagine_a25_check('neutral_counts_preserved', $n['comments']['all'] === $a['comments']['all']
        && $n['comments']['account'] === $a['comments']['account'] && $n['guests'] === $a['guests']);
    $five = array_fill(0, 5, $rows[0]);
    $b = Analysis::analyse($five, [], array_fill(0, 5, 2025), false);
    imagine_a25_check('five_native_status_year_visible', $b['comments']['all'] === [
        'groups' => [['year' => 2023, 'state' => '1', 'count' => 5]], 'autres' => 0]);
    imagine_a25_check('five_guest_year_visible', $b['guests'] === [
        'groups' => [['year' => 2025, 'state' => 'guest', 'count' => 5]], 'autres' => 0]);
    $bad = $rows[0];
    $bad['state'] = 'A25_PRIVATE_CANARY';
    $bad['year'] = 0;
    $c = Analysis::analyse(array_fill(0, 5, $bad), [], [], false);
    imagine_a25_check('unknown_native_status_closed', $c['comments']['all']['groups'][0] === [
        'year' => 0, 'state' => 'autre', 'count' => 5]);
    imagine_a25_check('no_free_text', !str_contains(json_encode($c), 'CANARY'));
    imagine_a25_check('empty_means_zero_only_without_marker', Analysis::analyse([], [], [], false)['forms']
        === ['groups' => [], 'autres' => 0]);
} catch (Throwable $error) {
    $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'detail' => get_class($error)];
}
$result = ['suite' => 'A25-pure', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
if (getenv('A25_PURE_INCLUDE') !== '1') {
    file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
    echo 'A25_UNIT ' . count($checks) . "\n";
    exit($result['exit_code']);
}
