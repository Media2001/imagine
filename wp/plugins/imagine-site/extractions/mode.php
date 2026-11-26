<?php

declare(strict_types=1);

use Imagine\Site\ExtractionsRegles;

return [
    'titre' => 'Abonnés par mode de paiement', 'disponible' => true,
    'colonnes' => ExtractionsRegles::COLONNES,
    'filtres' => ['mode_paiement' => ['label' => 'Mode de paiement', 'type' => 'select',
        'options' => ['' => 'Tous (y compris non renseigné)', 'bacs' => 'Virement',
            'imagine_papier' => 'Domiciliation papier', 'stripe' => 'Carte Stripe', 'stripe_sepa' => 'SEPA Stripe',
            'paypal' => 'PayPal']]],
    'requete' => ['subscription_status' => 'any'],
    'selection' => static fn (array $row, array $f): bool => $f['mode_paiement'] === '' || $row['mode_paiement'] === $f['mode_paiement'],
];
