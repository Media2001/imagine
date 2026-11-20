<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

/** Un backend de confiance ; les clés opaques incluent IP, robot et politique. */
interface Cache
{
    public function lire(string $cle): ?EntreeCache;

    public function ecrire(string $cle, EntreeCache $entree): void;
}
