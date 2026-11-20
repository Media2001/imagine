<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

use DateTimeImmutable;

/** C-03 / §3.9 et §4.4 : une identité seulement, jamais un droit au contenu. */
final readonly class Verificateur
{
    public function __construct(
        private Configuration $configuration,
        private Dns $dns,
        private CacheMemoire $cache,
        private HorlogeMonotone $horloge,
    ) {
    }

    public function verifier(string $agent, string $ip, DateTimeImmutable $maintenant): Decision
    {
        return new Decision(Motif::AgentInconnu);
    }
}
