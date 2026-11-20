<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use DateTimeImmutable;
use LogicException;

final readonly class Entry
{
    public function __construct(
        public Event $event,
        public State $state = State::Pending,
        public int $attempts = 0,
        public ?DateTimeImmutable $retryAt = null,
        public ?string $rule = null,
        public ?string $message = null,
        public ?DateTimeImmutable $leaseUntil = null
    ) {
    }

    public function transition(
        State $next,
        ?DateTimeImmutable $retryAt = null,
        ?string $rule = null,
        ?string $message = null,
        ?DateTimeImmutable $leaseUntil = null
    ): self {
        if (!$this->state->allows($next)) {
            throw new LogicException('Transition de file interdite.');
        }
        return new self(
            $this->event,
            $next,
            $this->attempts + ($next === State::Processing ? 1 : 0),
            $retryAt,
            $rule,
            $message,
            $leaseUntil
        );
    }
}
