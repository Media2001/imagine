<?php

declare(strict_types=1);

namespace Imagine\NonRegression\Tests;

use Imagine\NonRegression\Policy;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use RuntimeException;

final class PolicyTest extends TestCase
{
    public function testDsnSupportsSocketHostAndBoundedPorts(): void
    {
        self::assertSame('mysql:unix_socket=/scratch/mysql.sock;dbname=a03;charset=utf8mb4', Policy::dsn(
            ['DB_HOST' => 'localhost:/scratch/mysql.sock', 'DB_NAME' => 'a03']
        ));
        foreach (['db' => '3306', 'db:1' => '1', 'db:65535' => '65535'] as $host => $port) {
            self::assertSame('mysql:host=db;port=' . $port . ';dbname=a03;charset=utf8mb4', Policy::dsn(
                ['DB_HOST' => $host, 'DB_NAME' => 'a03']
            ));
        }
    }

    #[DataProvider('unsafeDsns')]
    public function testDsnRejectsInjectionAndOutOfRangePorts(string $host, string $database, string $code): void
    {
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage($code);
        Policy::dsn(['DB_HOST' => $host, 'DB_NAME' => $database]);
    }

    public static function unsafeDsns(): iterable
    {
        foreach (['db;host=other', 'db:0', 'db:65536', 'db:123456', 'localhost:/x;dbname=other'] as $host) {
            yield $host => [$host, 'a03', 'A03_DB_HOST'];
        }
        yield 'database injection' => ['db', 'a03;host=other', 'A03_DB_NAME'];
    }

    public function testVerifiedMarkerRequiresAllThreeStrictSignals(): void
    {
        $good = ['status' => 'verified', 'offline_verified' => true, 'runtime_probe_passed' => true];
        self::assertTrue(Policy::verified($good));
        foreach (array_keys($good) as $key) {
            $bad = $good;
            unset($bad[$key]);
            self::assertFalse(Policy::verified($bad));
            $bad[$key] = $key === 'status' ? 'pending' : 1;
            self::assertFalse(Policy::verified($bad));
        }
    }

    public function testRenewalRequiresTheThreeExplicitGates(): void
    {
        foreach ([false, true] as $requested) {
            foreach ([false, true] as $verified) {
                foreach ([false, true] as $safe) {
                    self::assertSame($requested && $verified && $safe, Policy::renewalAllowed(
                        $requested,
                        $verified,
                        $safe
                    ));
                }
            }
        }
    }
}
