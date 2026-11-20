<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

final readonly class Robot
{
    /** @param list<string> $agents @param list<string> $domaines */
    public function __construct(
        public string $identifiant,
        public array $agents,
        public Methode $methode,
        public array $domaines = [],
    ) {
    }
}
