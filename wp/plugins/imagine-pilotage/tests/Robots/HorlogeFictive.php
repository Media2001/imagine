<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Robots;

use Imagine\Pilotage\Robots\HorlogeMonotone;

final class HorlogeFictive implements HorlogeMonotone
{
    public int $temps = 0;

    public function millisecondes(): int
    {
        return $this->temps;
    }
}
