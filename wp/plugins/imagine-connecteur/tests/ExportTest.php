<?php

declare(strict_types=1);

namespace Imagine\Connecteur\Tests;

use DateTimeImmutable;
use Imagine\Connecteur\DailyCsvDestination;
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

final class ExportTest extends TestCase
{
    private string $directory;

    protected function setUp(): void
    {
        // PHPUnit supplies /work; every temporary artifact stays inside this explicit folder.
        $this->directory = dirname(__DIR__) . '/test-output-' . bin2hex(random_bytes(8));
        mkdir($this->directory);
    }

    protected function tearDown(): void
    {
        foreach (glob($this->directory . '/*') ?: [] as $path) {
            is_link($path) || is_file($path) ? unlink($path) : null;
        }
        foreach (glob($this->directory . '/.*') ?: [] as $path) {
            if (is_file($path) || is_link($path)) {
                unlink($path);
            }
        }
        rmdir($this->directory);
    }

    private function event(string $id, string $date): Event
    {
        $sample = EventTest::event();
        return new Event(EventType::OrderPaid, $id, new DateTimeImmutable($date), $sample->content);
    }

    private function destination(): DailyCsvDestination
    {
        return new DailyCsvDestination(
            $this->directory,
            new FrozenClock(new DateTimeImmutable('2026-11-20T12:00:00+01:00'))
        );
    }

    private function rows(string $day): array
    {
        $handle = fopen($this->directory . '/' . $day . '.csv', 'rb');
        $rows = [];
        $header = fgetcsv($handle, escape: '');
        while (($row = fgetcsv($handle, escape: '')) !== false) {
            $rows[] = array_combine($header, $row);
        }
        fclose($handle);
        return $rows;
    }

    public function testPersistentIdempotentExportRebuildsIdenticallyAndCatchesUpSkippedDays(): void
    {
        $destination = $this->destination();
        $one = $this->event('fiction-one', '2026-11-18T22:59:59Z');
        $two = $this->event('fiction-two', '2026-11-18T23:00:00Z');
        $today = $this->event('fiction-today', '2026-11-19T23:00:00Z');
        foreach ([$today, $two, $one, $two] as $event) {
            $destination->send($event, 5);
        }
        $now = new DateTimeImmutable('2026-11-20T00:00:00+01:00');
        $destination->exportPreviousDay($now);
        self::assertCount(1, $this->rows('2026-11-18'));
        self::assertCount(1, $this->rows('2026-11-19'));
        self::assertFileDoesNotExist($this->directory . '/2026-11-20.csv');
        $before = file_get_contents($this->directory . '/2026-11-19.csv');
        $restarted = $this->destination();
        $restarted->send($two, 5);
        $restarted->exportPreviousDay($now);
        self::assertSame($before, file_get_contents($this->directory . '/2026-11-19.csv'));
        $restarted->exportPreviousDay($now->modify('+1 day'));
        $all = [...$this->rows('2026-11-18'), ...$this->rows('2026-11-19'), ...$this->rows('2026-11-20')];
        self::assertCount(3, $all);
        self::assertCount(3, array_unique(array_column($all, 'idempotency_key')));
        self::assertSame($two->key(), $this->rows('2026-11-19')[0]['idempotency_key']);
        self::assertSame($two->content['total_minor'], (int) $this->rows('2026-11-19')[0]['total_minor']);
        self::assertSame($two->content['lines'], json_decode($this->rows('2026-11-19')[0]['lines_json'], true));
    }

    public function testSpringAndAutumnLocalDaysDoNotAssumeTwentyFourHours(): void
    {
        $destination = $this->destination();
        $cases = [
            '2026-03-29' => [
                '2026-03-28T23:00:00Z', '2026-03-29T00:59:59Z',
                '2026-03-29T01:00:00Z', '2026-03-29T21:59:59Z',
            ],
            '2026-10-25' => [
                '2026-10-24T22:00:00Z', '2026-10-25T00:30:00Z',
                '2026-10-25T01:30:00Z', '2026-10-25T22:59:59Z',
            ],
        ];
        foreach ($cases as $day => $dates) {
            foreach ($dates as $index => $date) {
                $destination->send($this->event('fiction-' . $day . '-' . $index, $date), 5);
            }
            $now = new DateTimeImmutable($day . 'T23:00:00Z');
            $now = $now->modify('+2 hours');
            $destination->exportPreviousDay($now);
            self::assertCount(4, $this->rows($day));
            foreach ($this->rows($day) as $row) {
                self::assertSame($day, substr($row['occurred_at'], 0, 10));
            }
        }
    }

    public function testQueueValidatesBeforeCsvAndRepeatedWorkerRunDoesNotAppend(): void
    {
        $queue = new InMemoryQueue();
        $destination = $this->destination();
        $clock = new FrozenClock(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        $worker = new Worker(
            $queue,
            $destination,
            $clock,
            new InMemoryAlerts(),
            Validator::billing(['fiction']),
            new RetryPolicy(3, 10, 2, 100),
            5
        );
        $sample = EventTest::event();
        $invalid = new Event(
            $sample->type,
            'fiction-invalid',
            $sample->occurredAt,
            array_replace($sample->content, ['total_minor' => 0])
        );
        $queue->add($sample);
        $queue->add($invalid);
        $worker->run();
        $worker->run();
        $destination->exportPreviousDay($clock->now());
        self::assertCount(1, $this->rows('2026-11-19'));
        self::assertSame(State::Quarantine, $queue->get($invalid->key())->state);
    }

    public function testLateEventUsesNextOpenBatchWithoutChangingAnAlreadyPublishedDay(): void
    {
        $destination = $this->destination();
        $now = new DateTimeImmutable('2026-11-20T12:00:00+01:00');
        $one = $this->event('fiction-one', '2026-11-19T11:00:00+01:00');
        $late = $this->event('fiction-late', '2026-11-19T12:00:00+01:00');
        $destination->send($one, 5);
        $destination->exportPreviousDay($now);
        $bytes = file_get_contents($this->directory . '/2026-11-19.csv');
        $destination->send($late, 5);
        $destination->send($late, 5);
        $destination->exportPreviousDay($now->modify('+1 day'));
        self::assertCount(1, $this->rows('2026-11-19'));
        self::assertCount(1, $this->rows('2026-11-20'));
        self::assertSame($late->key(), $this->rows('2026-11-20')[0]['idempotency_key']);
        self::assertStringStartsWith('2026-11-19', $this->rows('2026-11-20')[0]['occurred_at']);
        $destination->exportPreviousDay($now->modify('+1 day'));
        self::assertSame($bytes, file_get_contents($this->directory . '/2026-11-19.csv'));
    }

    public function testSymlinkCannotRedirectAnExportOutsideItsExplicitDirectory(): void
    {
        $outside = dirname($this->directory) . '/fiction-outside-' . bin2hex(random_bytes(8));
        file_put_contents($outside, 'unchanged-fiction');
        symlink($outside, $this->directory . '/2026-11-19.csv');
        try {
            $destination = $this->destination();
            $destination->exportPreviousDay(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
            self::fail('Le lien symbolique devait être refusé.');
        } catch (\Imagine\Connecteur\TemporaryFailure $exception) {
            self::assertSame('unchanged-fiction', file_get_contents($outside));
        } finally {
            unlink($outside);
        }
    }

    public function testCorruptJournalFailsClosedInsteadOfProducingAnIncompleteCsv(): void
    {
        $destination = $this->destination();
        $event = EventTest::event();
        $destination->send($event, 5);
        file_put_contents($this->directory . '/' . $event->key() . '.event.json', '{broken-fiction');
        $this->expectException(\JsonException::class);
        try {
            $destination->exportPreviousDay(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        } finally {
            self::assertFileDoesNotExist($this->directory . '/2026-11-19.csv');
        }
    }

    public function testEmptyDayStillHasStableColumns(): void
    {
        $destination = $this->destination();
        $destination->exportPreviousDay(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        self::assertSame([], $this->rows('2026-11-19'));
        $header = str_getcsv(trim(file_get_contents($this->directory . '/2026-11-19.csv')), escape: '');
        self::assertSame(DailyCsvDestination::COLUMNS, $header);
    }
}
