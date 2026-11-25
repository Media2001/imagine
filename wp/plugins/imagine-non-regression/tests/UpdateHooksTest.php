<?php

declare(strict_types=1);

namespace Imagine\NonRegression\Tests;

use Imagine\NonRegression\Report;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class UpdateHooksTest extends TestCase
{
    private const HOOK = 'woocommerce_run_on_woocommerce_admin_updated';

    public function testOnlyObservedAdminHookAndItsCounterAreExpectedAfterWooUpdate(): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['versions']['woocommerce'] = '11.1.1';
        $after['actions'][22] = ['hook' => self::HOOK, 'date' => '2026-11-25 00:00:00'];
        $after['action_days'][self::HOOK . ':2026-11-25'] = 1;
        $diff = Report::compare($before, $after);
        self::assertSame(0, $diff['anormal']);
        self::assertSame(['attendu', 'attendu', 'attendu'], array_column($diff['changes'], 'class'));
    }

    #[DataProvider('otherHooks')]
    public function testOtherActionsRemainAnomalousEvenDuringAnUpdate(string $hook): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['versions']['woocommerce'] = '11.1.1';
        $after['actions'][22] = ['hook' => $hook, 'date' => '2026-11-25 00:00:00'];
        $after['action_days'][$hook . ':2026-11-25'] = 1;
        self::assertSame(2, Report::compare($before, $after)['anormal']);
    }

    public static function otherHooks(): iterable
    {
        foreach (
            [
                'woocommerce_run_update_callback', 'action_scheduler/migration_hook',
                'woocommerce_scheduled_subscription_payment', self::HOOK . '_extra',
                'prefix_' . self::HOOK,
            ] as $hook
        ) {
            yield $hook => [$hook];
        }
    }

    public function testExpectedHookDoesNotHideAnUnrelatedActionOrAccessRegression(): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['versions']['woocommerce'] = '11.1.1';
        $after['actions'][22] = ['hook' => self::HOOK, 'date' => '2026-11-25 00:00:00'];
        $after['action_days'][self::HOOK . ':2026-11-25'] = 1;
        unset($after['actions'][1]);
        $after['access']['20:30'] = true;
        self::assertSame(2, Report::compare($before, $after)['anormal']);
    }

    public function testHookChangeWithoutWooUpdateRemainsAnomalous(): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['actions'][22] = ['hook' => self::HOOK, 'date' => '2026-11-25 00:00:00'];
        $after['action_days'][self::HOOK . ':2026-11-25'] = 1;
        self::assertSame(2, Report::compare($before, $after)['anormal']);
    }

    public function testReplacingAnUnrelatedHookWithTheExpectedHookIsAnomalous(): void
    {
        $before = Reports::photo();
        $after = $before;
        $after['versions']['woocommerce'] = '11.1.1';
        $after['actions'][1]['hook'] = self::HOOK;
        self::assertSame(1, Report::compare($before, $after)['anormal']);
    }
}
