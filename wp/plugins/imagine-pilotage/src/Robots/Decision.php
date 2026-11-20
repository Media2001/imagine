<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

final readonly class Decision
{
    public function __construct(public Motif $motif, public ?string $robot = null)
    {
    }

    public function estVerifie(): bool
    {
        return false;
    }
}
