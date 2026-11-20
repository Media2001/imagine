<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use InvalidArgumentException;

final class FakeDestination implements Destination
{
    private array $events = [];
    private array $timeouts = [];
    private int $calls = 0;

    /** Script: ok, down, slow (no effect), late_ack (effect then timeout), refuse. */
    public function __construct(private array $script = [])
    {
        foreach ($script as $action) {
            if (!in_array($action, ['ok', 'down', 'slow', 'late_ack', 'refuse'], true)) {
                throw new InvalidArgumentException('Action de destination fictive inconnue.');
            }
        }
    }

    public function send(Event $event, int $timeoutSeconds): void
    {
        ++$this->calls;
        $this->timeouts[] = $timeoutSeconds;
        if (isset($this->events[$event->key()])) {
            return;
        }
        $action = array_shift($this->script) ?? 'ok';
        if ($action === 'refuse') {
            throw new PermanentFailure('Donnée refusée par la destination fictive.');
        }
        if (in_array($action, ['down', 'slow'], true)) {
            throw new TemporaryFailure('Destination fictive indisponible ou délai dépassé.');
        }
        $this->events[$event->key()] = $event;
        if ($action === 'late_ack') {
            throw new TemporaryFailure('Accusé de réception perdu après écriture fictive.');
        }
    }

    public function accepted(): array
    {
        return $this->events;
    }

    public function calls(): int
    {
        return $this->calls;
    }

    public function timeouts(): array
    {
        return $this->timeouts;
    }
}
