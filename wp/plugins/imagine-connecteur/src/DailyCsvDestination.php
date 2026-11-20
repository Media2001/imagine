<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use DateTimeImmutable;
use DateTimeZone;
use InvalidArgumentException;

final readonly class DailyCsvDestination implements Destination
{
    public const COLUMNS = [
        'idempotency_key', 'type', 'source_id', 'occurred_at', 'subscription_id',
        'name', 'email', 'street', 'postal_code', 'city', 'country', 'enterprise_number',
        'currency', 'payment_method', 'payment_reference', 'total_minor', 'lines_json', 'batch_day',
    ];

    private string $directory;

    /** The existing directory must be private, trusted, writable and backed up. */
    public function __construct(string $directory, private Clock $clock)
    {
        $real = realpath($directory);
        if ($real === false || !is_dir($real) || !is_writable($real)) {
            throw new InvalidArgumentException('Le dossier d’export doit exister et être accessible en écriture.');
        }
        $this->directory = $real;
    }

    public function send(Event $event, int $timeoutSeconds): void
    {
        if ($timeoutSeconds < 1) {
            throw new InvalidArgumentException('Le délai d’envoi doit être positif.');
        }
        $this->locked(function () use ($event): void {
            $file = $this->path($event->key() . '.event.json');
            if (is_file($file)) {
                // First immutable event wins, even if its acknowledgement was lost.
                return;
            }
            $record = [
                'idempotency_key' => $event->key(), 'type' => $event->type->value,
                'source_id' => $event->sourceId, 'occurred_at' => $event->occurredAt->format('Y-m-d\TH:i:s.uP'),
                'subscription_id' => $event->subscriptionId, 'content' => $event->content,
                'batch_day' => $this->openBatch($event),
            ];
            $this->atomic($file, json_encode($record, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE));
        }, $timeoutSeconds);
    }

    /**
     * Export the preceding Brussels calendar day and catch up earlier journal days.
     * Published files are sealed; no append, no event changes its assigned partition.
     * Late arrivals join an open batch, retaining their original occurrence timestamp.
     *
     * @return array<string, string> day => absolute path
     */
    public function exportPreviousDay(DateTimeImmutable $now, int $timeoutSeconds = 5): array
    {
        $local = $now->setTimezone(new DateTimeZone('Europe/Brussels'));
        $yesterday = $local->setTime(0, 0)->modify('-1 day')->format('Y-m-d');
        return $this->locked(function () use ($yesterday): array {
            $days = [$yesterday => []];
            foreach (glob($this->directory . '/*.event.json') ?: [] as $file) {
                $this->path(basename($file));
                $record = json_decode($this->read($file), true, flags: JSON_THROW_ON_ERROR);
                $this->checkRecord($record, basename($file));
                $day = $record['batch_day'];
                if ($day <= $yesterday) {
                    $days[$day][] = $record;
                }
            }
            ksort($days);
            $paths = [];
            foreach ($days as $day => $records) {
                usort($records, static function (array $left, array $right): int {
                    $order = new DateTimeImmutable($left['occurred_at'])
                        <=> new DateTimeImmutable($right['occurred_at']);
                    return $order
                        ?: strcmp($left['idempotency_key'], $right['idempotency_key']);
                });
                $file = $this->path($day . '.csv');
                $bytes = $this->csv($records);
                if (is_file($file)) {
                    if ($this->read($file) !== $bytes) {
                        throw new TemporaryFailure('Un export scellé diffère du journal ; intervention requise.');
                    }
                } else {
                    $this->atomic($file, $bytes);
                }
                $paths[$day] = $file;
            }
            return $paths;
        }, $timeoutSeconds);
    }

    private function openBatch(Event $event): string
    {
        $day = $event->occurredAt->format('Y-m-d');
        if (is_file($this->path($day . '.csv'))) {
            $local = $this->clock->now()->setTimezone(new DateTimeZone('Europe/Brussels'))->setTime(0, 0);
            while (is_file($this->path($local->format('Y-m-d') . '.csv'))) {
                $local = $local->modify('+1 day');
            }
            $day = $local->format('Y-m-d');
        }
        return $day;
    }

    private function checkRecord(mixed $record, string $filename): void
    {
        if (
            !is_array($record)
            || !isset($record['idempotency_key'], $record['occurred_at'], $record['content'], $record['batch_day'])
            || !is_string($record['batch_day'])
            || preg_match('/^\d{4}-\d{2}-\d{2}$/D', $record['batch_day']) !== 1
            || !is_string($record['idempotency_key'])
            || $filename !== $record['idempotency_key'] . '.event.json'
            || preg_match('/^[0-9a-f]{64}$/D', $record['idempotency_key']) !== 1
        ) {
            throw new TemporaryFailure('Journal d’export incohérent ; intervention requise.');
        }
        $event = new Event(
            EventType::from($record['type']),
            $record['source_id'],
            new DateTimeImmutable($record['occurred_at']),
            $record['content'],
            $record['subscription_id']
        );
        if (
            $event->key() !== $record['idempotency_key']
            || $event->occurredAt->format('Y-m-d\TH:i:s.uP') !== $record['occurred_at']
        ) {
            throw new TemporaryFailure('Journal d’export incohérent ; intervention requise.');
        }
    }

    private function csv(array $records): string
    {
        $stream = fopen('php://memory', 'w+b');
        fputcsv($stream, self::COLUMNS, escape: '', eol: "\n");
        foreach ($records as $record) {
            $content = $record['content'];
            $identity = $content['identity'] ?? [];
            $address = $content['address'] ?? [];
            $row = [
                $record['idempotency_key'], $record['type'], $record['source_id'],
                $record['occurred_at'], $record['subscription_id'] ?? '',
                $identity['name'] ?? '', $identity['email'] ?? '', $address['street'] ?? '',
                $address['postal_code'] ?? '', $address['city'] ?? '', $address['country'] ?? '',
                $content['enterprise_number'] ?? '', $content['currency'] ?? '',
                $content['payment_method'] ?? '', $content['payment_reference'] ?? '',
                $content['total_minor'] ?? '',
                json_encode($content['lines'] ?? [], JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE),
                $record['batch_day'],
            ];
            fputcsv($stream, $row, escape: '', eol: "\n");
        }
        rewind($stream);
        $bytes = stream_get_contents($stream);
        fclose($stream);
        return $bytes;
    }

    private function path(string $basename): string
    {
        if ($basename === '' || basename($basename) !== $basename || str_contains($basename, '\\')) {
            throw new TemporaryFailure('Chemin d’export interdit.');
        }
        $path = $this->directory . DIRECTORY_SEPARATOR . $basename;
        if (is_link($path) || (file_exists($path) && !is_file($path))) {
            throw new TemporaryFailure('Cible d’export non régulière ou lien symbolique interdit.');
        }
        return $path;
    }

    private function read(string $file): string
    {
        $content = @file_get_contents($file);
        if ($content === false) {
            throw new TemporaryFailure('Lecture du journal d’export impossible.');
        }
        return $content;
    }

    private function locked(callable $operation, int $timeoutSeconds): mixed
    {
        if ($timeoutSeconds < 1) {
            throw new InvalidArgumentException('Le délai du verrou doit être positif.');
        }
        $handle = @fopen($this->path('.export.lock'), 'c+b');
        if ($handle === false) {
            throw new TemporaryFailure('Verrou d’export indisponible.');
        }
        $deadline = hrtime(true) + $timeoutSeconds * 1_000_000_000;
        try {
            while (!flock($handle, LOCK_EX | LOCK_NB)) {
                if (hrtime(true) >= $deadline) {
                    throw new TemporaryFailure('Délai du verrou d’export dépassé.');
                }
                usleep(1000);
            }
            return $operation();
        } finally {
            flock($handle, LOCK_UN);
            fclose($handle);
        }
    }

    private function atomic(string $target, string $content): void
    {
        $temporary = $this->path('.write-' . bin2hex(random_bytes(16)));
        $handle = @fopen($temporary, 'x+b');
        if ($handle === false) {
            throw new TemporaryFailure('Création du fichier d’export impossible.');
        }
        try {
            $length = strlen($content);
            $offset = 0;
            while ($offset < $length) {
                $written = fwrite($handle, substr($content, $offset));
                if ($written === false || $written === 0) {
                    throw new TemporaryFailure('Écriture de l’export interrompue.');
                }
                $offset += $written;
            }
            if (!fflush($handle) || !fsync($handle)) {
                throw new TemporaryFailure('Synchronisation de l’export impossible.');
            }
            fclose($handle);
            $handle = null;
            if (!@rename($temporary, $target)) {
                throw new TemporaryFailure('Publication atomique de l’export impossible.');
            }
        } finally {
            if (is_resource($handle)) {
                fclose($handle);
            }
            if (is_file($temporary)) {
                unlink($temporary);
            }
        }
    }
}
