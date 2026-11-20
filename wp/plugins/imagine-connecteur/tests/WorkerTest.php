<?php

declare(strict_types=1);

namespace Imagine\Connecteur\Tests;

use DateTimeImmutable;
use Imagine\Connecteur\Event;
use Imagine\Connecteur\EventType;
use Imagine\Connecteur\FakeDestination;
use Imagine\Connecteur\FrozenClock;
use Imagine\Connecteur\InMemoryAlerts;
use Imagine\Connecteur\InMemoryQueue;
use Imagine\Connecteur\RetryPolicy;
use Imagine\Connecteur\State;
use Imagine\Connecteur\Validator;
use Imagine\Connecteur\Worker;
use PHPUnit\Framework\TestCase;

final class WorkerTest extends TestCase
{
    private function bench(array $script = [], int $maxAttempts = 5): array
    {
        $queue = new InMemoryQueue();
        $clock = new FrozenClock(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        $alerts = new InMemoryAlerts();
        $destination = new FakeDestination($script);
        $worker = new Worker(
            $queue,
            $destination,
            $clock,
            $alerts,
            Validator::billing(['fiction']),
            new RetryPolicy($maxAttempts, 10, 2, 120),
            5
        );
        return [$queue, $clock, $alerts, $destination, $worker];
    }

    public function testThreeFailuresThenRecoverySendsOnlyOnceAndHonoursBackoff(): void
    {
        [$queue, $clock, , $destination, $worker] = $this->bench(['down', 'down', 'down', 'ok']);
        $event = EventTest::event();
        $queue->add($event);
        foreach ([10, 20, 40] as $delay) {
            self::assertSame(1, $worker->run());
            $entry = $queue->get($event->key());
            self::assertSame(State::TemporaryFailure, $entry->state);
            self::assertSame($clock->now()->getTimestamp() + $delay, $entry->retryAt->getTimestamp());
            self::assertSame(0, $worker->run(), 'No busy loop before the next retry.');
            $clock->advance($delay);
        }
        self::assertSame(1, $worker->run());
        self::assertSame(State::Sent, $queue->get($event->key())->state);
        self::assertSame(4, $queue->get($event->key())->attempts);
        self::assertCount(1, $destination->accepted());
        self::assertSame(4, $destination->calls());
        self::assertFalse($worker->replay($event->key()));
        self::assertSame(0, $worker->run());
        self::assertSame(4, $destination->calls());
        self::assertSame([5, 5, 5, 5], $destination->timeouts());
    }

    public function testLateAcknowledgementUsesDestinationIdempotency(): void
    {
        [$queue, $clock, , $destination, $worker] = $this->bench(['late_ack', 'ok']);
        $event = EventTest::event();
        $queue->add($event);
        $worker->run();
        self::assertSame(State::TemporaryFailure, $queue->get($event->key())->state);
        self::assertCount(1, $destination->accepted(), 'The remote side accepted before the timeout.');
        $clock->advance(10);
        $worker->run();
        self::assertSame(State::Sent, $queue->get($event->key())->state);
        self::assertCount(1, $destination->accepted());
        self::assertSame(2, $destination->calls());
    }

    public function testQuarantineBlocksOnlyItsOwnSubscriptionAndNamesTheRule(): void
    {
        [$queue, , $alerts, $destination, $worker] = $this->bench();
        $sample = EventTest::event();
        $invalid = new Event(
            EventType::SubscriptionCreated,
            'fiction-invalid',
            $sample->occurredAt,
            array_replace($sample->content, ['total_minor' => 999]),
            'fiction-sub-a'
        );
        $next = new Event(
            EventType::SubscriptionRenewed,
            'fiction-next',
            $sample->occurredAt->modify('+1 hour'),
            $sample->content,
            'fiction-sub-a'
        );
        $other = EventTest::event('fiction-other');
        foreach ([$next, $other, $invalid] as $event) {
            $queue->add($event);
        }
        self::assertSame(2, $worker->run());
        self::assertSame(State::Quarantine, $queue->get($invalid->key())->state);
        self::assertSame('amounts', $queue->get($invalid->key())->rule);
        self::assertNotEmpty($queue->get($invalid->key())->message);
        self::assertSame(State::Pending, $queue->get($next->key())->state);
        self::assertSame(State::Sent, $queue->get($other->key())->state);
        self::assertCount(1, $destination->accepted());
        self::assertSame('quarantine', $alerts->all()[0]['code']);
    }

    public function testPermanentRefusalQuarantinesWithoutRetry(): void
    {
        [$queue, $clock, $alerts, $destination, $worker] = $this->bench(['refuse']);
        $event = EventTest::event();
        $queue->add($event);
        $worker->run();
        $clock->advance(1000);
        self::assertSame(0, $worker->run());
        self::assertSame(State::Quarantine, $queue->get($event->key())->state);
        self::assertSame('destination', $queue->get($event->key())->rule);
        self::assertSame(1, $destination->calls());
        self::assertCount(1, $alerts->all());
    }

    public function testAttemptLimitAlertsOnceAndRetainsEvent(): void
    {
        [$queue, $clock, $alerts, $destination, $worker] = $this->bench(['down', 'down'], 2);
        $event = EventTest::event();
        $queue->add($event);
        $worker->run();
        $clock->advance(10);
        $worker->run();
        $clock->advance(1000);
        self::assertSame(0, $worker->run());
        self::assertSame(0, $worker->run());
        self::assertCount(1, $queue->all());
        self::assertSame(State::TemporaryFailure, $queue->get($event->key())->state);
        self::assertNull($queue->get($event->key())->retryAt);
        self::assertSame('attempts_exhausted', $alerts->all()[0]['code']);
        self::assertCount(1, $alerts->all());
        self::assertSame(2, $destination->calls());
    }

    public function testRetryDelayStartsAfterFailureNotBeforeSlowSend(): void
    {
        [$queue, $clock, $alerts] = $this->bench();
        $destination = new class ($clock) implements \Imagine\Connecteur\Destination {
            public function __construct(private FrozenClock $clock)
            {
            }

            public function send(Event $event, int $timeoutSeconds): void
            {
                $this->clock->advance(6);
                throw new \Imagine\Connecteur\TemporaryFailure('Délai fictif dépassé.');
            }
        };
        $worker = new Worker(
            $queue,
            $destination,
            $clock,
            $alerts,
            Validator::billing(['fiction']),
            new RetryPolicy(3, 10, 2, 100),
            5
        );
        $event = EventTest::event();
        $queue->add($event);
        $worker->run();
        self::assertSame($clock->now()->getTimestamp() + 10, $queue->get($event->key())->retryAt->getTimestamp());
    }

    public function testExpiredProcessingLeaseCanRecoverAfterWorkerCrash(): void
    {
        [$queue, $clock, , $destination, $worker] = $this->bench();
        $event = EventTest::event();
        $queue->add($event);
        $entry = $queue->get($event->key());
        $processing = $entry->transition(State::Processing, leaseUntil: $clock->now()->modify('+5 seconds'));
        $queue->replace($entry, $processing);
        self::assertSame(0, $worker->run());
        $clock->advance(5);
        self::assertSame(0, $worker->run());
        self::assertSame(State::TemporaryFailure, $queue->get($event->key())->state);
        $clock->advance(10);
        self::assertSame(1, $worker->run());
        self::assertSame(State::Sent, $queue->get($event->key())->state);
        self::assertCount(1, $destination->accepted());
    }

    public function testFutureEventsWaitAndSlowDestinationDoesNotLoseTheEvent(): void
    {
        [$queue, $clock, , $destination, $worker] = $this->bench(['slow', 'ok']);
        $sample = EventTest::event();
        $future = new Event($sample->type, 'fiction-future', $clock->now()->modify('+1 second'), $sample->content);
        $queue->add($future);
        self::assertSame(0, $worker->run());
        $clock->advance(1);
        self::assertSame(1, $worker->run());
        self::assertSame(State::TemporaryFailure, $queue->get($future->key())->state);
        self::assertCount(0, $destination->accepted());
        $clock->advance(10);
        self::assertSame(1, $worker->run());
        self::assertCount(1, $destination->accepted());
    }

    public function testSubscriptionEventsRunChronologicallyNotInsertionOrder(): void
    {
        [$queue, $clock, , $destination, $worker] = $this->bench(['down']);
        $sample = EventTest::event();
        $early = new Event($sample->type, 'fiction-early', $sample->occurredAt, $sample->content, 'fiction-sub');
        $later = new Event(
            EventType::SubscriptionRenewed,
            'fiction-later',
            $sample->occurredAt->modify('+1 hour'),
            $sample->content,
            'fiction-sub'
        );
        $queue->add($later);
        $queue->add($early);
        self::assertFalse($worker->replay($later->key()));
        self::assertSame(1, $worker->run());
        self::assertSame(State::Pending, $queue->get($later->key())->state);
        $clock->advance(10);
        self::assertSame(2, $worker->run());
        self::assertSame([$early->key(), $later->key()], array_keys($destination->accepted()));
    }
}
