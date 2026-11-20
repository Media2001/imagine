<?php

declare(strict_types=1);

// Fictitious, offline example. The only argument is an existing private output folder.
require dirname(__DIR__) . '/vendor/autoload.php';

use Imagine\Connecteur\DailyCsvDestination;
use Imagine\Connecteur\Event;
use Imagine\Connecteur\EventType;
use Imagine\Connecteur\FrozenClock;
use Imagine\Connecteur\InMemoryAlerts;
use Imagine\Connecteur\InMemoryQueue;
use Imagine\Connecteur\RetryPolicy;
use Imagine\Connecteur\Validator;
use Imagine\Connecteur\Worker;

if ($argc !== 2) {
    throw new InvalidArgumentException('Fournir uniquement le dossier privé de sortie.');
}
$clock = new FrozenClock(new DateTimeImmutable('2026-11-20T00:00:00+01:00'));
$destination = new DailyCsvDestination($argv[1], $clock);
$queue = new InMemoryQueue();
$alerts = new InMemoryAlerts();
$event = new Event(
    EventType::OrderPaid,
    'commande-fictive-demo',
    new DateTimeImmutable('2026-11-19T12:00:00+01:00'),
    [
        'identity' => ['name' => 'Personnage Fictif', 'email' => 'fiction@example.org'],
        'address' => ['street' => '1 rue Imaginaire', 'postal_code' => '0000',
            'city' => 'Ville Fictive', 'country' => 'BE'],
        'lines' => [['product' => 'Produit fictif', 'amount_minor' => 1200]],
        'total_minor' => 1200,
        'currency' => 'EUR',
        'payment_method' => 'fiction',
    ]
);
$worker = new Worker(
    $queue,
    $destination,
    $clock,
    $alerts,
    Validator::billing(['fiction']),
    new RetryPolicy(4, 10, 2, 120),
    5
);
$queue->add($event);
$queue->add($event);
$worker->run();
$paths = $destination->exportPreviousDay($clock->now());
$path = $paths['2026-11-19'];
$first = hash_file('sha256', $path);
$destination->exportPreviousDay($clock->now());
$second = hash_file('sha256', $path);
echo json_encode([
    'queue_entries' => count($queue->all()),
    'state' => $queue->get($event->key())->state->value,
    'replay_sent' => $worker->replay($event->key()),
    'alerts' => $alerts->all(),
    'export_sha256' => $second,
    'identical_after_rerun' => $first === $second,
], JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT) . "\n";
