<?php

declare(strict_types=1);

namespace Imagine\NonRegression\Tests;

use Imagine\NonRegression\PhpLog;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use RuntimeException;

final class PhpLogTest extends TestCase
{
    private string $file;
    private const FROM = '2026-11-25T12:00:00Z';
    private const UNTIL = '2026-11-25T12:00:02Z';

    protected function setUp(): void
    {
        $this->file = tempnam(sys_get_temp_dir(), 'a03-log-');
    }

    protected function tearDown(): void
    {
        if (is_file($this->file) || is_link($this->file)) {
            unlink($this->file);
        }
        if (is_link($this->file . '-link')) {
            unlink($this->file . '-link');
        }
    }

    public function testProbeIsBracketedByUtcTimestampsAndItsSilentLogIsCounted(): void
    {
        [$result, $log] = PhpLog::during($this->file, function (): string {
            file_put_contents($this->file, '[' . gmdate('d-M-Y H:i:s') . " UTC] PHP Warning: SILENT_CANARY\n");
            return 'healthy-http-200';
        });
        self::assertSame('healthy-http-200', $result);
        self::assertSame(1, $log['errors']);
        self::assertLessThanOrEqual(PhpLog::timestamp($log['until_utc']), PhpLog::timestamp($log['from_utc']));
    }

    public function testRotationDuringProbeIsBlocking(): void
    {
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_PHP_LOG_READ');
        PhpLog::during($this->file, function (): void {
            rename($this->file, $this->file . '-link');
            file_put_contents($this->file, '');
            unlink($this->file . '-link');
        });
    }

    public function testTruncationOrRewriteDuringProbeIsBlocking(): void
    {
        file_put_contents($this->file, "[24-Nov-2026 00:00:00 UTC] PHP Warning: old\n");
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_PHP_LOG_READ');
        PhpLog::during($this->file, function (): void {
            file_put_contents($this->file, "[24-Nov-2026 00:00:00 UTC] PHP Warning: new\n");
        });
    }

    public function testEmptyReadableLogIsACompleteZeroResult(): void
    {
        self::assertSame(['checked' => true, 'from_utc' => self::FROM,
            'until_utc' => self::UNTIL, 'errors' => 0], PhpLog::read($this->file, self::FROM, self::UNTIL));
    }

    public function testBothUtcBoundsAreInclusiveAndNoMessageOrPathEscapes(): void
    {
        file_put_contents($this->file, implode("\n", [
            '[25-Nov-2026 11:59:59 UTC] PHP Warning: old PERSONAL_LOG_CANARY',
            '[25-Nov-2026 12:00:00 UTC] PHP Warning: PERSONAL_LOG_CANARY@example.org',
            '[25-Nov-2026 12:00:01 UTC] PHP Fatal error: secret in /personal/path.php',
            'Stack trace:', '#0 /personal/path.php(1): example()', '  thrown in /personal/path.php on line 1',
            '[25-Nov-2026 12:00:02 UTC] PHP Notice: PERSONAL_LOG_CANARY',
            '[25-Nov-2026 12:00:03 UTC] PHP Warning: later PERSONAL_LOG_CANARY',
        ]) . "\n");
        $result = PhpLog::read($this->file, self::FROM, self::UNTIL);
        self::assertSame(3, $result['errors']);
        $json = json_encode($result, JSON_THROW_ON_ERROR);
        self::assertStringNotContainsString('PERSONAL_LOG_CANARY', $json);
        self::assertStringNotContainsString('/personal', $json);
        self::assertStringNotContainsString($this->file, $json);
    }

    #[DataProvider('invalidContents')]
    public function testUnparseableLogIsBlockingInsteadOfPartial(string $content): void
    {
        file_put_contents($this->file, $content);
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_PHP_LOG_FORMAT');
        PhpLog::read($this->file, self::FROM, self::UNTIL);
    }

    public static function invalidContents(): iterable
    {
        yield 'missing timestamp' => ["PERSONAL_LOG_CANARY\n"];
        yield 'unknown timezone' => ["[25-Nov-2026 12:00:01 Europe/Paris] PHP Warning: x\n"];
        yield 'invalid calendar date' => ["[31-Nov-2026 12:00:01 UTC] PHP Warning: x\n"];
        yield 'truncated record' => ['[25-Nov-2026 12:00:01 UTC] PHP Warning: x'];
        yield 'orphan trace' => ["#0 PERSONAL_LOG_CANARY\n"];
        yield 'unknown continuation' => ["[25-Nov-2026 12:00:01 UTC] PHP Warning: x\nPERSONAL\n"];
    }

    #[DataProvider('invalidWindows')]
    public function testInvalidWindowIsBlocking(string $from, string $until): void
    {
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_PHP_LOG_WINDOW');
        PhpLog::read($this->file, $from, $until);
    }

    public static function invalidWindows(): iterable
    {
        yield 'reverse' => [self::UNTIL, self::FROM];
        yield 'missing timezone' => ['2026-11-25 12:00:00', self::UNTIL];
        yield 'invalid date' => ['2026-11-31T12:00:00Z', self::UNTIL];
        yield 'unbounded' => ['2026-11-20T12:00:00Z', self::UNTIL];
    }

    public function testMissingLogIsNotAnEmptyLog(): void
    {
        unlink($this->file);
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_PHP_LOG_READ');
        PhpLog::read($this->file, self::FROM, self::UNTIL);
    }

    public function testUnreadableLogIsRefusedEvenUnderRoot(): void
    {
        chmod($this->file, 0000);
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_PHP_LOG_READ');
        PhpLog::read($this->file, self::FROM, self::UNTIL);
    }

    public function testSymlinkIsRefused(): void
    {
        symlink($this->file, $this->file . '-link');
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_PHP_LOG_READ');
        PhpLog::read($this->file . '-link', self::FROM, self::UNTIL);
    }

    public function testOversizedLogIsRefusedNotTruncated(): void
    {
        $stream = fopen($this->file, 'wb');
        ftruncate($stream, 16777217);
        fclose($stream);
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_PHP_LOG_READ');
        PhpLog::read($this->file, self::FROM, self::UNTIL);
    }
}
