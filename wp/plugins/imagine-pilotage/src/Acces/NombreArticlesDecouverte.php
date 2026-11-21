<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

final readonly class NombreArticlesDecouverte implements Decouverte
{
    use PerimetreDecouverte;

    public function __construct(public mixed $maximum, public mixed $numeros, public mixed $pdf)
    {
    }

    public function estValide(): bool
    {
        return is_int($this->maximum) && $this->maximum > 0 && $this->perimetreValide();
    }

    public function evaluer(array $contenu, array $droit, \DateTimeImmutable $instant): Motif
    {
        return $this->prerequis($contenu, $droit, $instant)
            ?? ($droit['consommes'] < $this->maximum ? Motif::DecouverteArticles : Motif::DecouverteEpuisee);
    }
}
