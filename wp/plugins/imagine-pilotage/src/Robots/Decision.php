<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

final readonly class Decision
{
    public function __construct(public Motif $motif, public ?string $robot = null)
    {
        $positif = in_array($motif, [Motif::VerifieDns, Motif::VerifiePlage], true);
        if ($positif !== ($robot !== null) || $robot === '') {
            throw new \InvalidArgumentException('Une identité est fournie uniquement pour un résultat positif.');
        }
    }

    public function estVerifie(): bool
    {
        return in_array($this->motif, [Motif::VerifieDns, Motif::VerifiePlage], true) && $this->robot !== null;
    }
}
