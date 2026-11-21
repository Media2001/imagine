<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

final readonly class DureeDecouverte implements Decouverte
{
    use PerimetreDecouverte;

    public function __construct(public mixed $secondes, public mixed $numeros, public mixed $pdf)
    {
    }

    public function estValide(): bool
    {
        return is_int($this->secondes) && $this->secondes > 0 && $this->perimetreValide();
    }

    public function evaluer(array $contenu, array $droit, \DateTimeImmutable $instant): Motif
    {
        return $this->prerequis($contenu, $droit, $instant)
            ?? ($instant->getTimestamp() - $droit['debut']->getTimestamp() < $this->secondes
                ? Motif::DecouverteDuree : Motif::DecouverteEpuisee);
    }
}
