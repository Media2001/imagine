<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

use DateTimeImmutable;
use DateTimeZone;

final readonly class Annee
{
    public DateTimeImmutable $debut;

    public ?DateTimeImmutable $ouverture;

    public function __construct(
        DateTimeImmutable $debut,
        public ?self $precedente = null,
        ?DateTimeImmutable $ouverture = null,
        public ?Activation $motif = null
    ) {
        $zone = new DateTimeZone('Europe/Brussels');
        $this->debut = $debut->setTimezone($zone);
        $this->ouverture = $ouverture?->setTimezone($zone);
        if (($ouverture === null) !== ($motif === null) || ($ouverture !== null && $ouverture < $debut)) {
            throw new \InvalidArgumentException('Activation sans motif ou antérieure à la commande.');
        }
    }

    public function activer(DateTimeImmutable $date, Activation $motif): self
    {
        if ($this->ouverture !== null) {
            throw new \LogicException('Année déjà activée : utiliser la réactivation après suspension.');
        }
        return new self($this->debut, $this->precedente, $date, $motif);
    }

    // Anniversaire isolé : interprétation provisoire du brief.
    public function finNumerique(): ?DateTimeImmutable
    {
        if ($this->ouverture?->format('m-d') === '02-29') {
            throw new \LogicException('Anniversaire du 29 février à arbitrer par Ced.');
        }
        return $this->ouverture?->modify('+1 year');
    }

    public function estActive(DateTimeImmutable $date): bool
    {
        return $this->ouverture !== null && $date >= $this->ouverture;
    }
}
