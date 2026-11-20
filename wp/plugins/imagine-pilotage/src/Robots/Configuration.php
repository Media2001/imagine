<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

final readonly class Configuration
{
    /** @param list<Robot> $robots */
    public function __construct(
        public array $robots,
        public int $delaiDnsMs = 200,
        public int $ttlPositif = 3600,
        public int $ttlNegatif = 60,
    ) {
    }
}
