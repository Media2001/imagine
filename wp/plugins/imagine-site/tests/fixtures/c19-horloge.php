<?php

declare(strict_types=1);

namespace Imagine\Site {
    // Only loaded in isolated PHPUnit children, never in WordPress.
    function time(): int
    {
        $GLOBALS['c19_clock_reads']++;
        return $GLOBALS['c19_clock'];
    }
}

namespace {
    function wc_get_orders(array $args): array
    {
        $GLOBALS['c19_clock'] += 2;
        return [];
    }

    function wcs_get_subscriptions(array $args): array
    {
        if ($args['subscription_status'] === 'any') {
            return [];
        }
        return [new class {
            public function get_id(): int { return 19; }
            public function get_customer_id(): int { return 19; }
            public function get_meta(string $key): string { return ''; }
            public function get_payment_method(): string { return 'bacs'; }
            public function get_status(): string { return 'active'; }
            public function get_billing_first_name(): string { return 'Fictif'; }
            public function get_billing_last_name(): string { return 'Horloge'; }
            public function get_total(): string { return '0'; }
            public function get_currency(): string { return 'EUR'; }
            public function get_time(string $key): int { return $key === 'next_payment' ? $GLOBALS['c19_due'] : 0; }
        }];
    }

    function wp_get_environment_type(): string
    {
        return 'test';
    }
}
