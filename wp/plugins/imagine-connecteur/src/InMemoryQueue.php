<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

final class InMemoryQueue implements QueueStorage
{
    /** @var array<string, Entry> */
    private array $entries = [];

    public function add(Event $event): bool
    {
        $key = $event->key();
        if (isset($this->entries[$key])) {
            return false;
        }
        $this->entries[$key] = new Entry($event);
        return true;
    }

    public function get(string $key): ?Entry
    {
        return $this->entries[$key] ?? null;
    }

    public function all(): array
    {
        return array_values($this->entries);
    }

    public function replace(Entry $expected, Entry $next): bool
    {
        $key = $expected->event->key();
        if (($this->entries[$key] ?? null) !== $expected || $next->event !== $expected->event) {
            return false;
        }
        if (!$expected->state->allows($next->state)) {
            throw new \LogicException('Transition de file interdite.');
        }
        $this->entries[$key] = $next;
        return true;
    }
}
