<?php

declare(strict_types=1);

namespace Imagine\Connecteur\Tests;

use DateTimeImmutable;
use Imagine\Connecteur\Event;
use Imagine\Connecteur\EventType;
use Imagine\Connecteur\InMemoryQueue;
use Imagine\Connecteur\State;
use InvalidArgumentException;
use LogicException;
use PHPUnit\Framework\TestCase;

final class EventTest extends TestCase
{
    public static function event(string $id = 'fiction-1', ?DateTimeImmutable $date = null): Event
    {
        return new Event(
            EventType::OrderPaid,
            $id,
            $date ?? new DateTimeImmutable('2026-11-19T12:00:00+01:00'),
            ['identity' => ['name' => 'Personnage Fictif', 'email' => 'fiction@example.org'],
                'address' => ['street' => '1 rue Imaginaire', 'postal_code' => '0000',
                    'city' => 'Ville Fictive', 'country' => 'BE'],
                'lines' => [['product' => 'Produit fictif', 'amount_minor' => 1200]],
                'total_minor' => 1200, 'currency' => 'EUR', 'payment_method' => 'fiction']
        );
    }

    public function testDeterministicIdentityAndDeduplicatedInsertion(): void
    {
        $first = self::event();
        $replay = self::event(date: new DateTimeImmutable('2026-11-20T15:00:00Z'));
        self::assertSame($first->key(), $replay->key());
        self::assertNotSame($first->key(), self::event('fiction-2')->key());
        $different = new Event(EventType::Refund, $first->sourceId, $first->occurredAt, $first->content);
        self::assertNotSame($first->key(), $different->key());
        $queue = new InMemoryQueue();
        self::assertTrue($queue->add($first));
        self::assertFalse($queue->add($replay));
        self::assertCount(1, $queue->all());
        self::assertSame($first, $queue->get($first->key())->event);
        self::assertSame('Europe/Brussels', $first->occurredAt->getTimezone()->getName());
    }

    public function testTransitionTableExhaustive(): void
    {
        $allowed = [
            'pending' => ['processing'],
            'processing' => ['sent', 'temporary_failure', 'quarantine'],
            'sent' => [],
            'temporary_failure' => ['processing'],
            'quarantine' => [],
        ];
        foreach (State::cases() as $from) {
            foreach (State::cases() as $to) {
                self::assertSame(in_array($to->value, $allowed[$from->value], true), $from->allows($to));
            }
        }
        $queue = new InMemoryQueue();
        $event = self::event();
        $queue->add($event);
        $entry = $queue->get($event->key());
        $processing = $entry->transition(State::Processing);
        self::assertSame(State::Pending, $entry->state);
        self::assertTrue($queue->replace($entry, $processing));
        self::assertFalse($queue->replace($entry, $processing), 'Stale claim must fail atomically.');
        $this->expectException(LogicException::class);
        $processing->transition(State::Pending);
    }

    public function testPrivacyWhitelistRejectsUnknownFieldsAtEveryLevel(): void
    {
        foreach (['preferences', 'identity', 'address', 'lines'] as $level) {
            $content = self::event()->content;
            if ($level === 'preferences') {
                $content['preferences'] = ['persona' => 'never transmit'];
            } elseif ($level === 'lines') {
                $content['lines'][0]['form_answers'] = 'never transmit';
            } else {
                $content[$level]['persona'] = 'never transmit';
            }
            try {
                new Event(EventType::OrderPaid, 'fiction', self::event()->occurredAt, $content);
                self::fail('Un champ hors facturation a été accepté.');
            } catch (InvalidArgumentException $exception) {
                self::assertStringNotContainsString('never transmit', $exception->getMessage());
            }
        }
    }

    public function testRenewalsRequireDistinctSourceObjectsNotJustSubscriptionId(): void
    {
        $date = self::event()->occurredAt;
        $one = new Event(EventType::SubscriptionRenewed, 'renewal-order-1', $date, [], 'subscription-fiction');
        $two = new Event(EventType::SubscriptionRenewed, 'renewal-order-2', $date, [], 'subscription-fiction');
        self::assertNotSame($one->key(), $two->key());
        $this->expectException(InvalidArgumentException::class);
        new Event(EventType::SubscriptionCreated, '', $date, []);
    }
}
