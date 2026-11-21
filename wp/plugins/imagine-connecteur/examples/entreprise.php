<?php

declare(strict_types=1);

require dirname(__DIR__) . '/vendor/autoload.php';

$validator = \Imagine\Connecteur\BillingComposition::withEntreprise(['fiction']);
$event = new \Imagine\Connecteur\Event(
    \Imagine\Connecteur\EventType::OrderPaid,
    'fiction-composition',
    new DateTimeImmutable('2026-11-21T10:00:00Z'),
    ['identity' => ['name' => 'Personnage Fictif'],
        'address' => ['street' => '1 rue Imaginaire', 'postal_code' => '0000',
            'city' => 'Ville Fictive', 'country' => 'BE'],
        'lines' => [['product' => 'Produit fictif', 'amount_minor' => 1200]],
        'total_minor' => 1200, 'currency' => 'EUR', 'payment_method' => 'fiction',
        'enterprise_number' => '0123456749']
);
echo json_encode(['violations' => count($validator->validate($event))], JSON_THROW_ON_ERROR) . PHP_EOL;
