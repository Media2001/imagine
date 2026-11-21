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
        public ?DateTimeImmutable $leaseUntil = null,
        public array $notifications = []
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
            $leaseUntil,
            $this->notifications
        );
    }

    public function withNotification(string $code, string $message): self
    {
        return $this->copyNotifications(array_replace($this->notifications, [$code => $message]));
    }

    public function acknowledge(string $code): self
    {
        $notifications = $this->notifications;
        unset($notifications[$code]);
        return $this->copyNotifications($notifications);
    }

    private function copyNotifications(array $notifications): self
    {
        return new self(
            $this->event,
            $this->state,
            $this->attempts,
            $this->retryAt,
            $this->rule,
            $this->message,
            $this->leaseUntil,
            $notifications
        );
    }

    public function sameBusinessState(self $other): bool
    {
        return $this->event === $other->event && $this->state === $other->state
            && $this->attempts === $other->attempts && $this->retryAt === $other->retryAt
            && $this->rule === $other->rule && $this->message === $other->message
            && $this->leaseUntil === $other->leaseUntil;
    }
}
