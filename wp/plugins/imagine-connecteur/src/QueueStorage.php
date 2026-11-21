<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

interface QueueStorage
{
    /** Atomic insert by key; divergent duplicates must persist a payload-free duplicate_content notification. */
    public function add(Event $event): bool;

    public function get(string $key): ?Entry;

    /** @return list<Entry> */
    public function all(): array;

    /**
     * Atomic CAS of the complete revision, including notifications with business transitions.
     * Notification-only acknowledgement preserves the business state; it is not a state transition.
     */
    public function replace(Entry $expected, Entry $next): bool;
}
