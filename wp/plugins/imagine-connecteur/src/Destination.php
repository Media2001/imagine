<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

interface Destination
{
    /**
     * Must enforce Event::key() atomically at the remote effect, including across timeouts.
     * Return means durable acknowledgement. A timeout must raise TemporaryFailure.
     */
    public function send(Event $event, int $timeoutSeconds): void;
}
