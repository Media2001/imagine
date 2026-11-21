<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Envoi;

use DateTimeImmutable;

final readonly class Situation
{
    /**
     * @param list<string> $numerosDus IDs fournis par C-01, jamais recalculés ici.
     * @param list<Destinataire> $destinataires Places attribuées uniquement.
     */
    public function __construct(
        public DateTimeImmutable $effet,
        public DateTimeImmutable $enregistre,
        public string $etat,
        public bool $paiementValide,
        public array $numerosDus,
        public array $destinataires,
        public ?DateTimeImmutable $fin = null
    ) {
        if (!in_array($etat, ['actif', 'grace', 'suspendu', 'expire', 'attente'], true)) {
            throw new \InvalidArgumentException('État inconnu.');
        }
        $ids = [];
        foreach ($destinataires as $destinataire) {
            if (!$destinataire instanceof Destinataire || isset($ids[$destinataire->id])) {
                throw new \InvalidArgumentException('Destinataire invalide ou attribué deux fois.');
            }
            $ids[$destinataire->id] = true;
        }
    }
}
