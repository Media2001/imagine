<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use PHPUnit\Framework\TestCase;

final class PacksC28AdapterTest extends TestCase
{
    public function testNativeHooksAgainstPersistedLightweightDoubles(): void
    {
        $fixture = __DIR__ . '/fixtures/c28-adapter.php';
        $process = proc_open([PHP_BINARY, $fixture], [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']], $pipes);
        self::assertIsResource($process);
        fclose($pipes[0]);
        $stdout = stream_get_contents($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        $exit = proc_close($process);
        self::assertSame('', $stderr);
        $result = json_decode($stdout, true, 512, JSON_THROW_ON_ERROR);
        self::assertNotEmpty($result['checks']);
        self::assertSame(count($result['checks']), $result['total']);
        foreach ($result['checks'] as $name => $ok) {
            self::assertTrue($ok, $name);
        }
        self::assertSame(0, $exit);
        self::assertSame(0, $result['failures']);
    }
}
