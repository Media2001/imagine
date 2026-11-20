<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use InvalidArgumentException;
use Throwable;

final readonly class Worker
{
    public function __construct(
        private QueueStorage $storage,
        private Destination $destination,
        private Clock $clock,
        private Alerts $alerts,
        private Validator $validator,
        private RetryPolicy $retry,
        private int $timeoutSeconds
    ) {
        if ($timeoutSeconds < 1) {
            throw new InvalidArgumentException('Le délai d’envoi doit être positif.');
        }
    }

    public function run(): int
    {
        $count = 0;
        foreach ($this->ordered() as $entry) {
            $count += $this->replay($entry->event->key()) ? 1 : 0;
        }
        return $count;
    }

    public function replay(string $key): bool
    {
        $entry = $this->storage->get($key);
        $now = $this->clock->now();
        if (
            $entry !== null && $entry->state === State::Processing
            && $entry->leaseUntil !== null && $entry->leaseUntil <= $now
        ) {
            $this->temporaryFailure($entry);
            return false;
        }
        if (
            $entry === null || !in_array($entry->state, [State::Pending, State::TemporaryFailure], true)
            || $entry->attempts >= $this->retry->maxAttempts || $entry->event->occurredAt > $now
            || ($entry->retryAt !== null && $entry->retryAt > $now) || $this->blocked($entry)
        ) {
            return false;
        }
        $processing = $entry->transition(
            State::Processing,
            leaseUntil: $now->setTimestamp($now->getTimestamp() + $this->timeoutSeconds)
        );
        if (!$this->storage->replace($entry, $processing)) {
            return false;
        }
        try {
            $violations = $this->validator->validate($entry->event);
            if ($violations !== []) {
                $this->quarantine($processing, $violations[0]->rule, $violations[0]->message);
                return true;
            }
            $this->destination->send($entry->event, $this->timeoutSeconds);
        } catch (PermanentFailure $exception) {
            $this->quarantine($processing, 'destination', 'La destination a refusé la donnée.');
            return true;
        } catch (Throwable $exception) {
            // Never persist raw remote errors: they may contain personal data or credentials.
            $this->temporaryFailure($processing);
            return true;
        }
        $this->storage->replace($processing, $processing->transition(State::Sent));
        return true;
    }

    private function temporaryFailure(Entry $entry): void
    {
        $now = $this->clock->now();
        $exhausted = $entry->attempts >= $this->retry->maxAttempts;
        $retryAt = $exhausted ? null : $now->setTimestamp(
            $now->getTimestamp() + $this->retry->delay($entry->attempts)
        );
        $failed = $entry->transition(
            State::TemporaryFailure,
            $retryAt,
            'transport',
            'Envoi non confirmé ; événement conservé dans la file.'
        );
        if ($this->storage->replace($entry, $failed) && $exhausted) {
            $this->alerts->notify(
                $entry->event->key(),
                'attempts_exhausted',
                'Limite d’essais atteinte ; intervention requise.'
            );
        }
    }

    private function quarantine(Entry $entry, string $rule, string $message): void
    {
        $next = $entry->transition(State::Quarantine, rule: $rule, message: $message);
        if ($this->storage->replace($entry, $next)) {
            $this->alerts->notify($entry->event->key(), 'quarantine', $rule . ' : ' . $message);
        }
    }

    /** @return list<Entry> */
    private function ordered(): array
    {
        $entries = $this->storage->all();
        usort($entries, self::compare(...));
        return $entries;
    }

    private static function compare(Entry $left, Entry $right): int
    {
        return ($left->event->occurredAt <=> $right->event->occurredAt)
            ?: strcmp($left->event->key(), $right->event->key());
    }

    private function blocked(Entry $entry): bool
    {
        $subscription = $entry->event->subscriptionId;
        if ($subscription === null) {
            return false;
        }
        foreach ($this->storage->all() as $other) {
            if (
                $other->event->subscriptionId === $subscription && $other->state !== State::Sent
                && self::compare($other, $entry) < 0
            ) {
                return true;
            }
        }
        return false;
    }
}
