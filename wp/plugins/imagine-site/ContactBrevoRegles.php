<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Projection pure. Les attributs personnels sont déjà filtrés par C24 en amont. */
final class ContactBrevoRegles
{
    public static function fiche(array $source): array
    {
        return ['fiche' => ['email' => $source['email'], 'statut' => 'abonne',
            'cooperateur' => $source['cooperateur'] ? 'oui' : 'non',
            'tarif' => $source['abonnements'][0]['tarifs'][0], 'newsletters' => ['principale'],
            'personnalisation' => $source['personnalisation']], 'raison' => 'eligible'];
    }
}
