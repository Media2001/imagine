<?php

declare(strict_types=1);

// Synthetic boundary schedules only; called during fixture construction.
add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
foreach (['2026-12-31 23:59:59', '2027-01-01 00:00:00', '2027-01-01 00:00:01'] as $next) {
    $sub = wcs_create_subscription([
        'customer_id' => (int) get_user_by('login', 'a02-admin')->ID,
        'status' => 'pending', 'billing_period' => 'month',
        'billing_interval' => 1, 'start_date' => '2026-01-01 00:00:00',
    ]);
    if (is_wp_error($sub)) {
        throw new RuntimeException('A32_CLOCK_FIXTURE');
    }
    $sub->set_requires_manual_renewal(true);
    $sub->set_payment_method('bacs');
    $sub->save();
    $sub->update_status('active');
    $sub->update_dates(['next_payment' => $next]);
}
$dates = [];
foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $sub) {
    if ($sub->get_status('edit') === 'active') {
        $dates[] = (int) $sub->get_time('next_payment', 'gmt');
    }
}
echo 'A32_CLOCK=' . json_encode(['active_next_native' => $dates], JSON_THROW_ON_ERROR) . "\n";
