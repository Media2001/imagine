<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

final readonly class Decision
{
    public function __construct(public bool $complet, public Motif $motif, public Bloc $bloc)
    {
    }
}
