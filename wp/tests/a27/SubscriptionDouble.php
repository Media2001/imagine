<?php

declare(strict_types=1);

namespace Imagine\Tests\SavedPayments;

/** Pure boundary double, aliased to WC_Subscription only in its own probe. */
final class SubscriptionDouble
{
    public function __call(string $name, array $arguments): mixed
    {
        return match ($name) {
            'get_payment_method' => 'ppcp-gateway',
            'get_payment_tokens' => [],
            default => throw new \BadMethodCallException('A27_TEST_METHOD'),
        };
    }
}
