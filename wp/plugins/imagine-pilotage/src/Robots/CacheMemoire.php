<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

/** Adaptateur de démonstration ; aucun stockage WordPress. */
final class CacheMemoire implements Cache
{
    /** @var array<string, EntreeCache> */
    private array $entrees = [];

    public function lire(string $cle): ?EntreeCache
    {
        return $this->entrees[$cle] ?? null;
    }

    public function ecrire(string $cle, EntreeCache $entree): void
    {
        $this->entrees[$cle] = $entree;
    }
}
