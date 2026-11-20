<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

final class InMemoryAlerts implements Alerts
{
    private array $notifications = [];

    public function notify(string $key, string $code, string $message): void
    {
        $this->notifications[$key . ':' . $code] = compact('key', 'code', 'message');
    }

    public function all(): array
    {
        return array_values($this->notifications);
    }
}
