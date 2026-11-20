<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

interface Alerts
{
    /** $key is an idempotency key; messages must not contain the billing payload. */
    public function notify(string $key, string $code, string $message): void;
}
