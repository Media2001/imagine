<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Echeancier;

/** Règles ouvertes C05, arbitrage du 22/11/2026. Aucun effet financier. */
final readonly class Reglages
{
    public function __construct(public ?int $margeJours = null)
    {
        if ($margeJours !== null && $margeJours < 1) {
            throw new \InvalidArgumentException('La marge civile doit être strictement positive.');
        }
    }
}
