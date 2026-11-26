<?php

declare(strict_types=1);

use Imagine\Site\ExtractionsRegles;

return [
    'titre' => 'Abonnés par état', 'disponible' => true,
    'colonnes' => ExtractionsRegles::COLONNES,
    // Valeurs = clés non traduites de MonCompteRegles::etat ; seuls les labels sont traduits à l'écran.
    'filtres' => ['etat' => ['label' => 'État', 'type' => 'select',
        'options' => ['' => 'Tous', 'Actif' => 'Actif', 'En délai de grâce' => 'En délai de grâce',
            'Suspendu' => 'Suspendu', 'Expiré' => 'Expiré']]],
    'requete' => ['subscription_status' => 'any'],
    'selection' => static fn (array $row, array $f): bool => $f['etat'] === '' || $row['etat'] === $f['etat'],
];
