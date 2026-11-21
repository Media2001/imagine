<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

interface Decouverte
{
    public function estValide(): bool;

    public function evaluer(array $contenu, array $droit, \DateTimeImmutable $instant): Motif;
}
