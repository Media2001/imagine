<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

final readonly class Reglages
{
    public function __construct(
        public bool $pdfRobotComplet = false,
        public bool $contenuFuturEquipe = false,
        public bool $pdfAnterieurAbonnement = false,
    ) {
    }
}
