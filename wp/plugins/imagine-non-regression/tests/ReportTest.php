<?php

declare(strict_types=1);

namespace Imagine\NonRegression\Tests;

use Imagine\NonRegression\Report;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use RuntimeException;

final class ReportTest extends TestCase
{
    public function testCompletePhotoAndTimestampAreSupported(): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['generated_at_utc'] = '2026-11-25T00:00:00+00:00';
        self::assertSame([], Report::compare($before, $after)['changes']);
    }

    #[DataProvider('malformedPhotos')]
    public function testIncompleteOrMistypedPhotoIsRefused(array $bad): void
    {
        foreach ([[$bad, Reports::photo()], [Reports::photo(), $bad]] as [$before, $after]) {
            try {
                Report::compare($before, $after);
                self::fail('Malformed report accepted');
            } catch (RuntimeException $error) {
                self::assertSame('A03_REPORT_STRUCTURE', $error->getMessage());
            }
        }
    }

    public static function malformedPhotos(): iterable
    {
        foreach (Reports::photo() as $key => $value) {
            if ($key === 'schema') {
                continue;
            }
            $bad = Reports::photo();
            unset($bad[$key]);
            yield 'missing ' . $key => [$bad];
            $bad = Reports::photo();
            $bad[$key] = is_array($value) ? 'not an array' : [];
            yield 'type ' . $key => [$bad];
        }
        foreach ([
            ['versions', 'wordpress'], ['sample_states', 'membership'],
            ['memberships', 1, 'status'], ['subscriptions', 9, 'next_payment_utc'],
            ['subscription_counts', 'status'], ['actions', 1, 'date'],
            ['orders', '2026-11:completed:EUR', 'amount_minor'], ['pages', 'home', 'final_status'],
            ['renewal', 'enabled'],
        ] as $path) {
            $bad = Reports::photo();
            $row = &$bad;
            foreach (array_slice($path, 0, -1) as $key) {
                $row = &$row[$key];
            }
            unset($row[$path[count($path) - 1]]);
            unset($row);
            yield 'nested missing ' . implode('.', $path) => [$bad];
        }
        foreach ([
            ['access', '10:30', 1], ['samples', 'none:none', '20'],
            ['sample_states', 'membership', ['none' => false]],
            ['pages', 'home', ['status' => '200', 'final_status' => 200, 'marker' => true, 'php_error' => false]],
            ['memberships', 1, ['user_id' => '10', 'plan_id' => 2, 'status' => 'active']],
            ['subscriptions', 9, ['status' => 'active', 'gateway' => 'manual', 'period' => 'month',
                'interval' => '1', 'next_payment_utc' => '']],
            ['actions', 1, ['hook' => 'example', 'date' => []]],
            ['orders', '2026-11:completed:EUR', ['count' => 1, 'amount_minor' => '15', 'decimals' => 2]],
            ['subscription_counts', 'status', ['active' => '1']],
        ] as [$section, $key, $value]) {
            $bad = Reports::photo();
            $bad[$section][$key] = $value;
            yield 'nested type ' . $section => [$bad];
        }
        $bad = Reports::photo();
        $bad['order_months'] = [];
        yield 'missing twelve month window' => [$bad];
        $bad = Reports::photo();
        $bad['storage'] = 'unknown';
        yield 'unknown storage' => [$bad];
    }

    public function testMinimalReportsAreRefused(): void
    {
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_REPORT_STRUCTURE');
        Report::compare(['schema' => 'imagine-a03-v1'], ['schema' => 'imagine-a03-v1']);
    }
}
