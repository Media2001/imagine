<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Echeancier;

use DateTimeImmutable;
use Imagine\Pilotage\Numeros\Numero;

final readonly class Versement
{
    public function __construct(
        public int $rang,
        public Numero $numero,
        public DateTimeImmutable $date,
        public bool $initial
    ) {
    }
}
