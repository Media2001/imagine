<?php

declare(strict_types=1);

namespace Imagine\NonRegression\Tests;

use Imagine\NonRegression\Policy;
use Imagine\NonRegression\Report;
use PHPUnit\Framework\TestCase;
use ReflectionClass;

final class PackageTest extends TestCase
{
    public function testPureClassesBelongToTheDiscoverablePackage(): void
    {
        foreach ([Report::class, Policy::class] as $class) {
            self::assertSame(
                dirname(__DIR__) . '/src/' . (new ReflectionClass($class))->getShortName() . '.php',
                (new ReflectionClass($class))->getFileName()
            );
        }
    }
}
