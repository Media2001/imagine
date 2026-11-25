<?php

declare(strict_types=1);

namespace Imagine\NonRegression\Tests;

final class Reports
{
    public static function photo(): array
    {
        $months = [];
        for ($month = 1; $month <= 12; $month++) {
            $months[] = sprintf('2026-%02d', $month);
        }
        $pages = [];
        foreach (['home', 'open', 'restricted', 'shop', 'cart', 'checkout', 'account'] as $page) {
            $pages[$page] = ['status' => 200, 'final_status' => 200, 'marker' => true, 'php_error' => false];
        }
        return [
            'schema' => 'imagine-a03-v1', 'generated_at_utc' => '2026-11-24T00:00:00+00:00',
            'versions' => ['wordpress' => '6.8.3', 'php' => '8.2.33', 'woocommerce' => '10.0',
                'memberships' => '1.0', 'subscriptions' => '1.0'],
            'storage' => 'classic',
            'sample_states' => ['membership' => ['active' => true, 'none' => true],
                'subscription' => ['active' => true, 'none' => true]],
            'samples' => ['active:active' => 10, 'none:none' => 20],
            'memberships' => [1 => ['user_id' => 10, 'plan_id' => 2, 'status' => 'active']],
            'access' => ['0:30' => false, '10:30' => true, '20:30' => false],
            'subscriptions' => [9 => ['status' => 'active', 'gateway' => 'manual', 'period' => 'month',
                'interval' => 1, 'next_payment_utc' => '2027-01-01 00:00:00']],
            'subscription_counts' => ['status' => ['active' => 1], 'gateway' => ['manual' => 1],
                'period' => ['1-month' => 1]],
            'actions' => [1 => ['hook' => 'woocommerce_scheduled_subscription_payment',
                'date' => '2027-01-01 00:00:00']],
            'action_days' => ['woocommerce_scheduled_subscription_payment:2027-01-01' => 1],
            'order_months' => $months,
            'orders' => ['2026-11:completed:EUR' => ['count' => 1, 'amount_minor' => 1500, 'decimals' => 2]],
            'php_log' => ['checked' => true, 'from_utc' => '2026-11-24T00:00:00Z',
                'until_utc' => '2026-11-24T00:00:01Z', 'errors' => 0],
            'pages' => $pages, 'renewal' => ['enabled' => false],
        ];
    }

    public static function probe(): array
    {
        return ['schema' => 'imagine-a03-v1', 'mode' => 'renewal_probe', 'renewal' => [
            'enabled' => true, 'manual_only' => true, 'created' => true,
            'linked' => true, 'pending' => true, 'cleaned' => true,
        ]];
    }
}
