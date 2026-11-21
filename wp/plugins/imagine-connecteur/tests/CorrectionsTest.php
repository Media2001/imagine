<?php

declare(strict_types=1);

namespace Imagine\Connecteur\Tests;

use DateTimeImmutable;
use Imagine\Connecteur\Alerts;
use Imagine\Connecteur\BillingComposition;
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
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class CorrectionsTest extends TestCase
{
    private string $directory;

    protected function setUp(): void
    {
        $this->directory = dirname(__DIR__) . '/test-corrections-' . bin2hex(random_bytes(8));
        mkdir($this->directory);
    }

    protected function tearDown(): void
    {
        foreach ([...glob($this->directory . '/*'), ...glob($this->directory . '/.*')] as $file) {
            if (is_file($file) || is_link($file)) {
                unlink($file);
            }
        }
        rmdir($this->directory);
    }

    private function worker(
        $queue,
        $destination,
        $clock,
        $alerts,
        ?Validator $validator = null,
        int $attempts = 1
    ): Worker {

        return new Worker(
            $queue,
            $destination,
            $clock,
            $alerts,
            $validator ?? Validator::billing(['fiction']),
            new RetryPolicy($attempts, 1, 2, 10),
            5
        );
    }

    public function testRattrapageMonotoneDurableEtOrdreDansLeCsv(): void
    {
        $clock = new FrozenClock(new DateTimeImmutable('2026-11-18T12:00:00+01:00'));
        $queue = new InMemoryQueue();
        $sample = EventTest::event();
        $creation = new Event(EventType::SubscriptionCreated, 'fiction-create', $clock->now(), $sample->content, 'sub-f');
        $queue->add($creation);
        $this->worker($queue, new FakeDestination(['down']), $clock, new InMemoryAlerts(), attempts: 3)->run();
        self::assertSame(State::TemporaryFailure, $queue->get($creation->key())->state);
        $clock->advance(86400);
        $destination = new DailyCsvDestination($this->directory, $clock);
        $destination->exportPreviousDay($clock->now());
        $renewal = new Event(EventType::SubscriptionRenewed, 'fiction-renew', $clock->now(), $sample->content, 'sub-f');
        $queue->add($renewal);
        $clock->advance(86400);
        $worker = $this->worker($queue, $destination, $clock, new InMemoryAlerts(), attempts: 3);
        self::assertSame(2, $worker->run());
        $restarted = new DailyCsvDestination($this->directory, $clock);
        $restarted->send($creation, 5);
        $restarted->send($renewal, 5);
        foreach ([$creation, $renewal] as $event) {
            $record = json_decode(file_get_contents($this->directory . '/' . $event->key() . '.event.json'), true);
            self::assertSame('2026-11-20', $record['batch_day']);
        }
        $restarted->exportPreviousDay($clock->now());
        $clock->advance(86400);
        $restarted->exportPreviousDay($clock->now());
        $csv = file_get_contents($this->directory . '/2026-11-20.csv');
        self::assertLessThan(strpos($csv, $renewal->key()), strpos($csv, $creation->key()));
        self::assertSame(1, substr_count($csv, $creation->key()));
        self::assertSame(1, substr_count($csv, $renewal->key()));
        $restarted->exportPreviousDay($clock->now());
        self::assertSame($csv, file_get_contents($this->directory . '/2026-11-20.csv'));
    }

    public function testInstantaneDetacheAvantValidationDepotEtJournal(): void
    {
        $sample = EventTest::event();
        $identity = $sample->content['identity'];
        $amount = 1200;
        $line = ['product' => 'Produit fictif', 'amount_minor' => &$amount];
        $total = 1200;
        $content = $sample->content;
        $content['identity'] = &$identity;
        $content['lines'] = [&$line];
        $content['total_minor'] = &$total;
        $event = new Event($sample->type, 'fiction-references', $sample->occurredAt, $content);
        $identity['name'] = 'Mutation fictive';
        $queue = new InMemoryQueue();
        $queue->add($event);
        $identity['preferences'] = 'INTERDIT-FICTIF';
        $line['form_answers'] = 'INTERDIT-FICTIF';
        $amount = 999;
        $total = 999;
        self::assertSame($sample->content, $event->content);
        self::assertSame($sample->content, $queue->get($event->key())->event->content);
        $clock = new FrozenClock(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        $destination = new DailyCsvDestination($this->directory, $clock);
        $this->worker($queue, $destination, $clock, new InMemoryAlerts())->run();
        $destination->exportPreviousDay($clock->now());
        foreach (glob($this->directory . '/*') as $file) {
            self::assertStringNotContainsString('INTERDIT-FICTIF', file_get_contents($file));
        }
        self::assertSame(State::Sent, $queue->get($event->key())->state);
    }

    #[DataProvider('notifications')]
    public function testAlerteSurvitPanneEtRedemarrageSansNouvelEnvoi(bool $quarantine): void
    {
        $queue = new InMemoryQueue();
        $clock = new FrozenClock(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        $sample = EventTest::event();
        $event = $quarantine ? new Event(
            $sample->type,
            'fiction-invalid',
            $sample->occurredAt,
            array_replace($sample->content, ['total_minor' => 999])
        ) : $sample;
        $queue->add($event);
        $destination = new FakeDestination(['down']);
        $alerts = new class implements Alerts {
            public int $calls = 0;
            public array $accepted = [];

            public function notify(string $key, string $code, string $message): void
            {
                if (++$this->calls === 1) {
                    throw new \RuntimeException('Panne fictive.');
                }
                $this->accepted[$key . ':' . $code] = $message;
            }
        };
        $this->worker($queue, $destination, $clock, $alerts)->run();
        $code = $quarantine ? 'quarantine' : 'attempts_exhausted';
        self::assertArrayHasKey($code, $queue->get($event->key())->notifications);
        $calls = $destination->calls();
        $restarted = $this->worker($queue, $destination, $clock, $alerts);
        self::assertSame(0, $restarted->run());
        self::assertSame([], $queue->get($event->key())->notifications);
        self::assertArrayHasKey($event->key() . ':' . $code, $alerts->accepted);
        self::assertSame(0, $restarted->run());
        self::assertSame(2, $alerts->calls);
        self::assertSame($calls, $destination->calls());
    }

    public static function notifications(): array
    {
        return [[true], [false]];
    }

    public function testCompositionAvecVraiC02EtQuarantaine(): void
    {
        $clock = new FrozenClock(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        $queue = new InMemoryQueue();
        $destination = new FakeDestination();
        $validator = BillingComposition::withEntreprise(['fiction']);
        foreach (['0123456749', '0123456700'] as $number) {
            $sample = EventTest::event();
            $event = new Event($sample->type, 'fiction-' . $number, $sample->occurredAt, array_replace(
                $sample->content,
                ['enterprise_number' => $number]
            ));
            $queue->add($event);
        }
        self::assertSame(2, $this->worker($queue, $destination, $clock, new InMemoryAlerts(), $validator)->run());
        self::assertCount(1, $destination->accepted());
        $quarantine = array_values(array_filter($queue->all(), fn ($e) => $e->state === State::Quarantine));
        self::assertCount(1, $quarantine);
        self::assertSame('enterprise_number', $quarantine[0]->rule);
    }

    public function testCsvNeutraliseFormulesMaisPasMontantsNumeriques(): void
    {
        $clock = new FrozenClock(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        $destination = new DailyCsvDestination($this->directory, $clock);
        $sample = EventTest::event();
        foreach (['=fiction', '+fiction', '-fiction', '@fiction', "\t=fiction", 'texte fictif'] as $index => $text) {
            $content = $sample->content;
            $content['identity']['name'] = $text;
            $content['total_minor'] = -1200;
            $content['lines'][0]['amount_minor'] = -1200;
            $event = new Event($sample->type, 'fiction-formula-' . $index, $sample->occurredAt, $content);
            $destination->send($event, 5);
        }
        $destination->exportPreviousDay($clock->now());
        $stream = fopen($this->directory . '/2026-11-19.csv', 'r');
        $header = fgetcsv($stream, escape: '');
        $names = [];
        while (($row = fgetcsv($stream, escape: '')) !== false) {
            $row = array_combine($header, $row);
            $names[] = $row['name'];
            self::assertSame('-1200', $row['total_minor']);
        }
        fclose($stream);
        foreach (["'=fiction", "'+fiction", "'-fiction", "'@fiction", "'\t=fiction", 'texte fictif'] as $name) {
            self::assertContains($name, $names);
        }
    }

    public function testDivergenceAlerteeSansRemplacerEvenement(): void
    {
        $queue = new InMemoryQueue();
        $first = EventTest::event();
        $queue->add($first);
        $other = new Event($first->type, $first->sourceId, $first->occurredAt, array_replace(
            $first->content,
            ['payment_reference' => 'fiction-divergente']
        ));
        self::assertFalse($queue->add($other));
        self::assertSame($first, $queue->get($first->key())->event);
        $clock = new FrozenClock(new DateTimeImmutable('2026-11-20T12:00:00+01:00'));
        $alerts = new InMemoryAlerts();
        $this->worker($queue, new FakeDestination(), $clock, $alerts)->run();
        self::assertSame('duplicate_content', $alerts->all()[0]['code']);
        self::assertStringNotContainsString('fiction-divergente', $alerts->all()[0]['message']);
    }

    public function testRetryPlafondMemeTresGrandNumeroDessai(): void
    {
        $retry = new RetryPolicy(9, 10, 2, 35);
        self::assertSame(10, $retry->delay(1));
        self::assertSame(20, $retry->delay(2));
        self::assertSame(35, $retry->delay(3));
        self::assertSame(35, $retry->delay(PHP_INT_MAX));
    }

    #[DataProvider('retryInvalides')]
    public function testRetryRefuseParametresInvalides(array $args, ?int $attempt): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $retry = new RetryPolicy(...$args);
        if ($attempt !== null) {
            $retry->delay($attempt);
        }
    }

    public static function retryInvalides(): array
    {
        return [[[0, 1, 2, 10], null], [[1, 0, 2, 10], null], [[1, 1, 1, 10], null],
            [[1, 10, 2, 9], null], [[1, 1, 2, 10], 0], [[1, 1, 2, 10], -1]];
    }
}
