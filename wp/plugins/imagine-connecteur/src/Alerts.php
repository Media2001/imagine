<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

interface Alerts
{
    /** Deduplicate persistently by ($key, $code), including lost ACKs; messages contain no billing payload. */
    public function notify(string $key, string $code, string $message): void;
}
