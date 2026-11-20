<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

use DateTimeImmutable;
use DateTimeZone;
use InvalidArgumentException;

final readonly class Numero
{
    public DateTimeImmutable $sortie;
    public DateTimeImmutable $cloture;

    public function __construct(
        public string $id,
        public TypeNumero $type,
        DateTimeImmutable $sortie,
        DateTimeImmutable $cloture
    ) {
        if ($id === '') {
            throw new InvalidArgumentException('Identifiant de numéro vide.');
        }
        $zone = new DateTimeZone('Europe/Brussels');
        $this->sortie = $sortie->setTimezone($zone)->setTime(0, 0);
        $this->cloture = $cloture->setTimezone($zone)->setTime(0, 0);
        if ($this->cloture > $this->sortie) {
            throw new InvalidArgumentException('La clôture doit précéder ou coïncider avec la sortie.');
        }
    }

    // Interprétation provisoire du brief : clôture incluse, à minuit Bruxelles.
    public function estCloture(DateTimeImmutable $date): bool
    {
        return $date >= $this->cloture;
    }
}
