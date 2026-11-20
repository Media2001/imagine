<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

interface HorlogeMonotone
{
    public function millisecondes(): int;
}
