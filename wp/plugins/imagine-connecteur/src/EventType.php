<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

enum EventType: string
{
    case OrderPaid = 'order_paid';
    case SubscriptionCreated = 'subscription_created';
    case SubscriptionRenewed = 'subscription_renewed';
    case Refund = 'refund';
}
