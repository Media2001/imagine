<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use Imagine\Pilotage\Entreprise\NumeroEntreprise;

/** Composition locale explicite, sans accès BCE/VIES ni dépendance du moteur à WordPress. */
final class BillingComposition
{
    public static function withEntreprise(array $knownPayments): Validator
    {
        return Validator::billing(
            $knownPayments,
            static fn (string $number): bool => NumeroEntreprise::depuisSaisie($number)->estValide()
        );
    }
}
