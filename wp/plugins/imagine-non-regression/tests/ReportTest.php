<?php

declare(strict_types=1);

namespace Imagine\NonRegression\Tests;

use Imagine\NonRegression\Report;
use PHPUnit\Framework\TestCase;
use RuntimeException;

final class ReportTest extends TestCase
{
    public function testMinimalReportsAreRefused(): void
    {
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_REPORT_STRUCTURE');
        Report::compare(['schema' => 'imagine-a03-v1'], ['schema' => 'imagine-a03-v1']);
    }
}
