<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

interface QueueStorage
{
    /** Atomically insert by key, preserving the first immutable event. */
    public function add(Event $event): bool;

    public function get(string $key): ?Entry;

    /** @return list<Entry> */
    public function all(): array;

    /** Atomic compare-and-swap: only the exact expected revision can be replaced. */
    public function replace(Entry $expected, Entry $next): bool;
}
