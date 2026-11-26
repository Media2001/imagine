<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\{EcheancesNatives, EcheancesRegles, TableauBordNatives};
use PHPUnit\Framework\Attributes\{PreserveGlobalState, RunTestsInSeparateProcesses};
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class TableauBordNativesTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/fixtures/c19-horloge.php';
        $GLOBALS['c19_clock'] = 1800000000;
        $GLOBALS['c19_clock_reads'] = 0;
        $GLOBALS['c19_due'] = $GLOBALS['c19_clock'] + 180 * 86400 + 1;
    }

    public function testSharedInstantIncludesRowCrossing180DayBoundaryDuringRead(): void
    {
        $reference = $GLOBALS['c19_clock'] + 2;
        $result = TableauBordNatives::lire($reference);
        $row = ['id' => 19, 'etat' => 'active', 'prochaine' => $GLOBALS['c19_due'], 'fin' => 0];
        self::assertGreaterThanOrEqual($reference, $GLOBALS['c19_clock']);
        foreach ([30, 90, 180] as $days) {
            $expected = count(EcheancesRegles::echeances([$row], $reference, $days));
            self::assertSame($expected, $result['echeances']['valeurs'][$days], 'Parité C15/C19 au même instant');
            self::assertCount($expected, EcheancesNatives::lire('echeances', $days, $reference));
        }
        self::assertSame(1, $result['echeances']['valeurs'][180]);
        self::assertSame(0, $GLOBALS['c19_clock_reads'], 'Un instant injecté ne relit pas l’horloge.');
    }

    public function testDefaultDashboardCapturesClockOnceBeforeNativeReads(): void
    {
        $result = TableauBordNatives::lire();
        self::assertSame(0, $result['echeances']['valeurs'][180]);
        self::assertSame(1, $GLOBALS['c19_clock_reads']);
    }
}
