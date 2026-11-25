<?php

declare(strict_types=1);

namespace Imagine\NonRegression\Tests;

use Imagine\NonRegression\Report;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use RuntimeException;

final class LogReportTest extends TestCase
{
    public function testLogWindowChangesAloneDoNotCreateNoise(): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['php_log']['from_utc'] = '2026-11-25T12:00:00Z';
        $after['php_log']['until_utc'] = '2026-11-25T12:00:02Z';
        self::assertSame([], Report::compare($before, $after)['changes']);
    }

    public function testSilentPhpDiagnosticIsAnomalousEvenWithHealthyHttpAndUnchangedCount(): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['php_log']['errors'] = 1;
        self::assertSame([['path' => 'php_log.errors', 'class' => 'anormal']], Report::compare(
            $before,
            $after
        )['changes']);
        self::assertSame(1, Report::compare($after, $after)['anormal']);
    }

    #[DataProvider('invalidLogs')]
    public function testMissingOrPartialLogResultIsNotAValidPhoto(array $log): void
    {
        $bad = Reports::photo();
        $bad['php_log'] = $log;
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_REPORT_STRUCTURE');
        Report::compare($bad, $bad);
    }

    public static function invalidLogs(): iterable
    {
        yield 'unchecked' => [['checked' => false, 'from_utc' => '2026-11-25T12:00:00Z',
            'until_utc' => '2026-11-25T12:00:02Z', 'errors' => 0]];
        yield 'partial' => [['checked' => true, 'errors' => 0]];
        yield 'negative' => [['checked' => true, 'from_utc' => '2026-11-25T12:00:00Z',
            'until_utc' => '2026-11-25T12:00:02Z', 'errors' => -1]];
        yield 'bad date' => [['checked' => true, 'from_utc' => '2026-11-31T12:00:00Z',
            'until_utc' => '2026-11-25T12:00:02Z', 'errors' => 0]];
        yield 'reverse' => [['checked' => true, 'from_utc' => '2026-11-25T12:00:02Z',
            'until_utc' => '2026-11-25T12:00:00Z', 'errors' => 0]];
    }
}
