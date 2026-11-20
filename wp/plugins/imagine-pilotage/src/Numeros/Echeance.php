<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

use DateTimeImmutable;

final readonly class Echeance
{
    public DateTimeImmutable $lancement;

    public function __construct(public Numero $numero, DateTimeImmutable $lancement)
    {
        $this->lancement = $lancement->setTimezone(new \DateTimeZone('Europe/Brussels'));
    }

    public function estPassee(DateTimeImmutable $reference): bool
    {
        return $this->lancement < $reference;
    }
}
