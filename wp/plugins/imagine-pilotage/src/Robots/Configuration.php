<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

final readonly class Configuration
{
    /** @param list<Robot> $robots */
    public function __construct(
        public array $robots,
        public int $delaiDnsMs = 1000,
        public int $ttlPositif = 3600,
        public int $ttlNegatif = 60,
    ) {
        if ($delaiDnsMs <= 0 || $ttlNegatif <= 0 || $ttlPositif <= $ttlNegatif) {
            throw new \InvalidArgumentException('Délais positifs requis, cache négatif plus court que le positif.');
        }
        $ids = [];
        $jetons = [];
        foreach ($robots as $robot) {
            if (!$robot instanceof Robot || isset($ids[$robot->identifiant])) {
                throw new \InvalidArgumentException('Robot invalide ou identifiant dupliqué.');
            }
            $ids[$robot->identifiant] = true;
            foreach ($robot->agents as $agent) {
                $agent = strtolower($agent);
                if (isset($jetons[$agent])) {
                    throw new \InvalidArgumentException('Jeton agent partagé par plusieurs robots.');
                }
                $jetons[$agent] = true;
            }
        }
    }
}
