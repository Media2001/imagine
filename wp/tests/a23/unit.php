<?php

declare(strict_types=1);

namespace Imagine\ReaderAccountsTest;

require '/subject/a23/Analysis.php';

use Imagine\ReaderAccounts\Analysis;

$checks = [];
function check(string $name, bool $ok): void
{
    global $checks;
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
    if (!$ok) {
        throw new \RuntimeException($name);
    }
}

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
        check('prefix_only:' . $expected . ':' . count($checks), Analysis::family($value) === $expected);
    }
    check('privacy_threshold', Analysis::pool(['phpass' => 5, 'bcrypt' => 4, 'autre' => 1, 'vide' => 0])
        === ['groups' => [['label' => 'phpass', 'accounts' => 5]], 'autres' => 5]);
    check('empty_threshold', Analysis::pool(['phpass' => 0]) === ['groups' => [], 'autres' => 0]);
} catch (\Throwable $error) {
    $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'class' => get_class($error)];
}
$result = ['suite' => 'A23-pure', 'checks' => $checks,
    'exit_code' => (int) (count(array_filter($checks, static fn(array $c): bool => $c['status'] === 'FAIL')) > 0)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
exit($result['exit_code']);
