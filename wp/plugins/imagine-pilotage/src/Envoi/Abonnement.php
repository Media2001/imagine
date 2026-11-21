<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Envoi;

use DateTimeImmutable;

final readonly class Abonnement
{
    /** @param list<Situation> $situations Historique complet, append-only. */
    public function __construct(
        public string $id,
        public string $origine,
        public DateTimeImmutable $creation,
        public array $situations
    ) {
        if (!in_array($origine, ['abonnement', 'offert', 'groupe', 'numero_unite'], true)) {
            throw new \InvalidArgumentException('Origine inconnue.');
        }
        $instants = [];
        foreach ($situations as $situation) {
            $instant = $situation->effet->format('U.u');
            if (isset($instants[$instant])) {
                throw new \InvalidArgumentException('Deux situations au même instant : historique ambigu.');
            }
            $instants[$instant] = true;
        }
    }
}
