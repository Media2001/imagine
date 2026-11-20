<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

use DateTimeImmutable;

final readonly class Echeance
{
    public function __construct(public Numero $numero, public DateTimeImmutable $lancement)
    {
    }

    public function estPassee(DateTimeImmutable $reference): bool
    {
        return $this->lancement < $reference;
    }
}
