<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Envoi;

final readonly class Destinataire
{
    public function __construct(
        public string $id,
        public string $nom,
        public string $rue,
        public string $complement,
        public string $codePostal,
        public string $ville,
        public string $pays
    ) {
    }
}
