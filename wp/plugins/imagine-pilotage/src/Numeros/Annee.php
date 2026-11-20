<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

use DateTimeImmutable;
use DateTimeZone;

final readonly class Annee
{
    public DateTimeImmutable $debut;

    public ?DateTimeImmutable $ouverture;

    private array $transitions;

    public function __construct(
        DateTimeImmutable $debut,
        public ?self $precedente = null,
        ?DateTimeImmutable $ouverture = null,
        public ?Activation $motif = null,
        array $transitions = []
    ) {
        $zone = new DateTimeZone('Europe/Brussels');
        $this->debut = $debut->setTimezone($zone);
        $this->ouverture = $ouverture?->setTimezone($zone);
        if (($ouverture === null) !== ($motif === null) || ($ouverture !== null && $ouverture < $debut)) {
            throw new \InvalidArgumentException('Activation sans motif ou antérieure à la commande.');
        }
        if ($precedente !== null && $debut <= $precedente->debut) {
            throw new \InvalidArgumentException('Le renouvellement doit suivre le début précédent.');
        }
        $derniere = $ouverture;
        $normalisees = [];
        foreach ($transitions as $transition) {
            if (!$transition instanceof DateTimeImmutable || $derniere === null || $transition <= $derniere) {
                throw new \InvalidArgumentException('Historique de suspension invalide.');
            }
            $normalisees[] = $transition->setTimezone($zone);
            $derniere = $transition;
        }
        $this->transitions = $normalisees;
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

    public function suspendre(DateTimeImmutable $date): self
    {
        return $this->transition($date, true);
    }

    public function reactiver(DateTimeImmutable $date): self
    {
        return $this->transition($date, false);
    }

    private function transition(DateTimeImmutable $date, bool $suspendre): self
    {
        $derniere = $this->transitions[array_key_last($this->transitions)] ?? $this->ouverture;
        $suspendue = count($this->transitions) % 2 === 1;
        if ($derniere === null || $date <= $derniere || $suspendue === $suspendre) {
            throw new \LogicException('Transition impossible ou non chronologique.');
        }
        $transitions = [...$this->transitions, $date->setTimezone(new DateTimeZone('Europe/Brussels'))];
        return new self($this->debut, $this->precedente, $this->ouverture, $this->motif, $transitions);
    }

    public function estActive(DateTimeImmutable $date): bool
    {
        if ($this->ouverture === null || $date < $this->ouverture) {
            return false;
        }
        $active = true;
        foreach ($this->transitions as $transition) {
            if ($transition > $date) {
                break;
            }
            $active = !$active;
        }
        return $active;
    }
}
