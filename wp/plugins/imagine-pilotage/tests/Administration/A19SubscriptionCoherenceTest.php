<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Administration;

use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

/** Pure A19 rules only: the classic/HPOS fixtures remain outside T01. */
final class A19SubscriptionCoherenceTest extends TestCase
{
    public static function a19Cases(): iterable
    {
        $wp = is_file('/repo/wp/tests/a19/unit.php') ? '/repo/wp' : dirname(__DIR__, 4);
        $checks = require $wp . '/tests/a19/unit.php';
        foreach ($checks as $check) {
            yield $check['check'] => [$check['status']];
        }
    }

    #[DataProvider('a19Cases')]
    public function testPureCoherenceRule(string $status): void
    {
        self::assertSame('PASS', $status);
    }
}
