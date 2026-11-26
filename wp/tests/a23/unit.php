<?php

declare(strict_types=1);

namespace Imagine\ReaderAccountsTest;

$path = dirname(__DIR__, 2) . '/outils/bascule/a23/Analysis.php';
if (!is_file($path)) {
    $path = '/subject/a23/Analysis.php';
}
require $path;

use Imagine\ReaderAccounts\Analysis;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
    if (!$ok) {
        throw new \RuntimeException($name);
    }
};

try {
    $families = [
        '$wp$2y$PRIVATE_CANARY' => 'wordpress_bcrypt', '$P$PRIVATE_CANARY' => 'phpass',
        '$H$PRIVATE_CANARY' => 'phpass_h', '$2y$PRIVATE_CANARY' => 'bcrypt',
        '$2a$PRIVATE_CANARY' => 'bcrypt', '$2b$PRIVATE_CANARY' => 'bcrypt',
        '$argon2i$PRIVATE_CANARY' => 'argon2i', '$argon2id$PRIVATE_CANARY' => 'argon2id',
        '01234567890123456789012345678901' => 'autre', '' => 'vide',
        'A23_HASH_PRIVATE_CANARY' => 'autre', '$wp$PRIVATE_CANARY' => 'autre',
    ];
    foreach ($families as $value => $expected) {
        $check('prefix_only:' . $expected . ':' . count($checks), Analysis::family($value) === $expected);
    }
    $check('privacy_threshold', Analysis::pool(['phpass' => 5, 'bcrypt' => 4, 'autre' => 1, 'vide' => 0])
        === ['groups' => [['label' => 'phpass', 'accounts' => 5]], 'autres' => 5]);
    $check('empty_threshold', Analysis::pool(['phpass' => 0]) === ['groups' => [], 'autres' => 0]);
    $rows = [];
    for ($i = 0; $i < 10; $i++) {
        $rows[] = ['id' => $i + 1, 'hash' => $i < 5 ? '$P$A23_PRIVATE_CANARY' : '$wp$2y$A23_PRIVATE_CANARY',
            'email' => 'fictif-' . $i . '@example.org', 'email_valid' => true,
            'login' => $i < 5 ? 'fictif-' . $i . '@example.org' : 'fictif-' . $i,
            'admin' => false, 'live' => $i < 5, 'commerce' => $i < 5];
    }
    $a = Analysis::analyse($rows, false);
    $check('families_exact', $a['readers']['families'] === ['groups' => [
        ['label' => 'phpass', 'accounts' => 5], ['label' => 'wordpress_bcrypt', 'accounts' => 5]], 'autres' => 0]);
    $check('accounts_unique', $a['readers']['accounts'] === 10 && $a['live_readers']['accounts'] === 5);
    $check('login_equals_exact', $a['readers']['logins'] === ['groups' => [
        ['label' => 'login_equals_email', 'accounts' => 5]], 'autres' => 0]);
    $check('without_any_commerce', $a['without_commerce'] === ['groups' => [
        ['label' => 'without_order_or_subscription', 'accounts' => 5]], 'autres' => 0]);
    $check('live_families_exact', $a['live_readers']['families'] === ['groups' => [
        ['label' => 'phpass', 'accounts' => 5]], 'autres' => 0]);
    $check('emails_empty', $a['readers']['emails'] === ['groups' => [], 'autres' => 0]);
    $rows[0]['email'] = '';
    $rows[0]['email_valid'] = false;
    $rows[1]['email'] = 'A23_EMAIL_PRIVATE_CANARY';
    $rows[1]['email_valid'] = false;
    $rows[2]['email'] = 'shared@example.org';
    $rows[3]['email'] = 'SHARED@example.org';
    $rows[2]['login'] = 'Case';
    $rows[3]['login'] = 'cASE';
    $a = Analysis::analyse($rows, false);
    $check('rare_email_metrics_pooled', $a['readers']['emails'] === ['groups' => [], 'autres' => 4]);
    $check('rare_login_metrics_pooled', $a['readers']['logins'] === ['groups' => [], 'autres' => 3]);
    $rows[] = ['id' => 11, 'hash' => 'A23_HASH_PRIVATE_CANARY', 'email' => 'fictif-4@example.org',
        'email_valid' => true, 'login' => 'CASE', 'admin' => true, 'live' => true, 'commerce' => true];
    $a = Analysis::analyse($rows, false);
    $check('admin_excluded_but_collision_included', $a['readers']['accounts'] === 10
        && $a['live_readers']['accounts'] === 5 && $a['readers']['emails']['autres'] === 5);
    $check('no_private_output', !str_contains(json_encode($a), 'CANARY') && !str_contains(json_encode($a), '@'));
    $n = Analysis::analyse($rows, true);
    foreach (['readers', 'live_readers'] as $scope) {
        foreach (['families', 'emails', 'logins'] as $key) {
            $check('neutralisation_unknown:' . $scope . ':' . $key,
                $n[$scope][$key] === 'inconnu après neutralisation');
        }
        $check('neutralisation_preserves_count:' . $scope, $n[$scope]['accounts'] === $a[$scope]['accounts']);
    }
    $check('neutralisation_preserves_links', $n['without_commerce'] === $a['without_commerce']);
    $check('empty_population', Analysis::analyse([], false)['readers']['accounts'] === 0);
} catch (\Throwable $error) {
    $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'class' => get_class($error)];
}
if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') !== __FILE__) {
    return $checks;
}
$result = ['suite' => 'A23-pure', 'checks' => $checks,
    'exit_code' => (int) (count(array_filter($checks, static fn(array $c): bool => $c['status'] === 'FAIL')) > 0)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
exit($result['exit_code']);
