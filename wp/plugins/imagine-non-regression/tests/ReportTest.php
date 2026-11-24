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

    public function testRenewalProbeHasItsOwnCompleteSchema(): void
    {
        $before = Reports::probe();
        self::assertSame([], Report::compare($before, $before)['changes']);
        $after = $before;
        $after['renewal']['cleaned'] = false;
        self::assertSame([['path' => 'renewal.cleaned', 'class' => 'a regarder']], Report::compare(
            $before,
            $after
        )['changes']);
    }

    #[DataProvider('invalidModesAndProbes')]
    public function testInvalidModesAndIncompleteProbesAreRefused(array $before, array $after, string $code): void
    {
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage($code);
        Report::compare($before, $after);
    }

    public static function invalidModesAndProbes(): iterable
    {
        yield 'photo to probe' => [Reports::photo(), Reports::probe(), 'A03_REPORT_MODE'];
        yield 'probe to photo' => [Reports::probe(), Reports::photo(), 'A03_REPORT_MODE'];
        foreach (Reports::probe()['renewal'] as $key => $value) {
            $bad = Reports::probe();
            unset($bad['renewal'][$key]);
            yield 'missing probe ' . $key => [$bad, $bad, 'A03_REPORT_STRUCTURE'];
            $bad = Reports::probe();
            $bad['renewal'][$key] = 1;
            yield 'mistyped probe ' . $key => [$bad, $bad, 'A03_REPORT_STRUCTURE'];
        }
        $bad = Reports::probe();
        $bad['renewal']['enabled'] = false;
        yield 'disabled probe' => [$bad, $bad, 'A03_REPORT_STRUCTURE'];
        $bad = Reports::photo();
        $bad['renewal']['enabled'] = true;
        yield 'enabled photo' => [$bad, $bad, 'A03_REPORT_STRUCTURE'];
        $bad = Reports::photo();
        $bad['mode'] = 'renewal_probe';
        yield 'hybrid' => [$bad, $bad, 'A03_REPORT_STRUCTURE'];
        $bad = Reports::probe();
        unset($bad['mode']);
        yield 'implicit probe' => [$bad, $bad, 'A03_REPORT_STRUCTURE'];
        foreach ([null, 'photo', 'unknown', [], 1] as $mode) {
            $bad = Reports::photo();
            $bad['mode'] = $mode;
            yield 'unknown mode ' . get_debug_type($mode) . json_encode($mode) => [$bad, $bad, 'A03_REPORT_MODE'];
        }
    }

    #[DataProvider('unsafeKeys')]
    public function testKeysAreCheckedPerSectionWithoutEchoingThem(array $bad): void
    {
        try {
            Report::compare($bad, $bad);
            self::fail('Unsafe key accepted');
        } catch (RuntimeException $error) {
            self::assertSame('A03_REPORT_STRUCTURE', $error->getMessage());
            self::assertStringNotContainsString('Jean', $error->getMessage());
        }
    }

    public static function unsafeKeys(): iterable
    {
        foreach ([
            ['access', 'Jean.Dupont', true], ['access', '-1:30', true], ['access', '1:0', true],
            ['memberships', 'Jean.Dupont', ['user_id' => 10, 'plan_id' => 2, 'status' => 'active']],
            ['subscriptions', 'Jean.Dupont', Reports::photo()['subscriptions'][9]],
            ['actions', 'Jean.Dupont', ['hook' => 'example', 'date' => '2027-01-01 00:00:00']],
            ['samples', 'Jean.Dupont', 20], ['samples', 'none:none:active', 20],
            ['pages', 'Jean.Dupont', Reports::photo()['pages']['home']],
            ['orders', 'Jean.Dupont', ['count' => 1, 'amount_minor' => 100, 'decimals' => 2]],
            ['orders', '2026-99:completed:EUR', ['count' => 1, 'amount_minor' => 100, 'decimals' => 2]],
            ['action_days', 'Jean Dupont:2027-01-01', 1], ['action_days', '../hook:2027-01-01', 1],
        ] as $index => [$section, $key, $value]) {
            $bad = Reports::photo();
            $bad[$section][$key] = $value;
            yield $section . $index => [$bad];
        }
        foreach ([['sample_states', 'membership'], ['sample_states', 'subscription'],
            ['subscription_counts', 'status'], ['subscription_counts', 'gateway'],
            ['subscription_counts', 'period']] as [$section, $group]) {
            $bad = Reports::photo();
            $bad[$section][$group]['Jean.Dupont'] = $section === 'sample_states' ? true : 1;
            yield $section . $group => [$bad];
        }
        $bad = Reports::photo();
        $bad['order_months'] = array_combine(range(20, 31), $bad['order_months']);
        yield 'non-list months' => [$bad];
        $bad = Reports::photo();
        $bad['order_months'][0] = 'Jean.Dupont';
        yield 'invalid month' => [$bad];
        $bad = Reports::photo();
        $bad['Jean.Dupont'] = true;
        yield 'unknown root' => [$bad];
        $bad = Reports::photo();
        $bad['pages']['home']['Jean.Dupont'] = true;
        yield 'unknown row field' => [$bad];
    }

    public function testSlugShapedPersonalKeysAndAllValuesAreMasked(): void
    {
        $before = Reports::photo();
        $before['samples']['jean-dupont:none'] = 1;
        $before['sample_states']['membership']['jean-dupont'] = true;
        $before['subscription_counts']['gateway']['jean-dupont'] = 1;
        $before['action_days']['Jean.Dupont:2027-01-01'] = 1;
        $before['orders']['2026-11:jean-dupont:EUR'] = ['count' => 1, 'amount_minor' => 1, 'decimals' => 2];
        $after = $before;
        $after['samples']['jean-dupont:none'] = 2;
        unset($after['sample_states']['membership']['jean-dupont']);
        $after['subscription_counts']['gateway']['jean-dupont'] = 2;
        $after['action_days']['Jean.Dupont:2027-01-01'] = 2;
        $after['orders']['2026-11:jean-dupont:EUR']['count'] = 2;
        $after['versions']['wordpress'] = 'PRIVATE_VALUE_CANARY';
        $json = json_encode(Report::compare($before, $after), JSON_THROW_ON_ERROR);
        self::assertStringNotContainsString('jean-dupont', $json);
        self::assertStringNotContainsString('Jean.Dupont', $json);
        self::assertStringNotContainsString('PRIVATE_VALUE_CANARY', $json);
        self::assertSame(5, Report::compare($before, $after)['anormal']);
    }

    public function testDisappearingPageIsAnomalous(): void
    {
        $before = Reports::photo();
        $after = $before;
        unset($after['pages']['home']);
        self::assertSame([['path' => 'pages.home', 'class' => 'anormal']], Report::compare(
            $before,
            $after
        )['changes']);
    }

    public function testExistingClassificationsRemainUnchanged(): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['versions']['wordpress'] = '6.9.1';
        $after['access']['10:30'] = false;
        unset($after['actions'][1]);
        $result = Report::compare($before, $after);
        self::assertSame(['attendu', 'anormal', 'anormal'], array_column($result['changes'], 'class'));
        self::assertSame(2, $result['anormal']);
        $after = $before;
        $after['pages']['home']['marker'] = false;
        $after['subscriptions'][9]['next_payment_utc'] = '2027-01-02 00:00:00';
        self::assertSame(2, Report::compare($before, $after)['anormal']);
        foreach (['status' => 302, 'final_status' => 500, 'php_error' => true] as $key => $value) {
            $after = $before;
            $after['pages']['home'][$key] = $value;
            self::assertSame($key === 'status' ? 'a regarder' : 'anormal', Report::compare(
                $before,
                $after
            )['changes'][0]['class']);
        }
        $after = $before;
        unset($after['sample_states']['membership']['active']);
        self::assertCount(1, Report::compare($before, $after)['changes']);
    }

    public function testMinimalReportsAreRefused(): void
    {
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('A03_REPORT_STRUCTURE');
        Report::compare(['schema' => 'imagine-a03-v1'], ['schema' => 'imagine-a03-v1']);
    }
}
