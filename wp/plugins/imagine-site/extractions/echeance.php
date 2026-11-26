<?php

declare(strict_types=1);

use Imagine\Site\ExtractionsRegles;

return [
    'titre' => 'Abonnés par date d’échéance', 'disponible' => true,
    'colonnes' => ExtractionsRegles::COLONNES,
    'filtres' => ['du' => ['label' => 'Du (UTC, inclus)', 'type' => 'date', 'defaut' => 'today'],
        'au' => ['label' => 'Au (UTC, inclus)', 'type' => 'date', 'defaut' => '+30 days']],
    'validation' => static fn (array $f): bool => $f['du'] <= $f['au'],
    'requete' => ['subscription_status' => 'any'],
    'selection' => static fn (array $row, array $f): bool => $row['echeance_utc'] !== ''
        && $row['echeance_utc'] >= $f['du'] . ' 00:00:00' && $row['echeance_utc'] <= $f['au'] . ' 23:59:59',
];
