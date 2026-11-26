<?php

declare(strict_types=1);

use Imagine\Site\ExtractionsRegles;

return [
    'titre' => 'Abonnés par localité', 'disponible' => true,
    'colonnes' => ExtractionsRegles::COLONNES,
    'filtres' => ['pays' => ['label' => 'Pays (code ISO, vide = tous)', 'type' => 'text', 'pattern' => '/^(?:[A-Z]{2})?$/D'],
        'code_postal' => ['label' => 'Code postal exact (vide = tous)', 'type' => 'text']],
    'requete' => ['subscription_status' => 'any'],
    'selection' => static fn (array $row, array $f): bool => ($f['pays'] === '' || $row['pays'] === $f['pays'])
        && ($f['code_postal'] === '' || $row['code_postal'] === $f['code_postal']),
];
