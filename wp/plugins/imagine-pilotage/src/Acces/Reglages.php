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

    public static function depuisOptions(mixed $options): self
    {
        if (!is_array($options)) {
            return new self();
        }
        return new self(
            pdfRobotComplet: ($options['pdf_robot'] ?? null) === 'complet',
            contenuFuturEquipe: ($options['contenu_futur'] ?? null) === 'equipe',
            pdfAnterieurAbonnement: ($options['pdf_anterieur_abonnement'] ?? null) === 'ouvert',
        );
    }

    public function options(): array
    {
        return [
            'contenu_futur' => $this->contenuFuturEquipe ? 'equipe' : 'ferme_tous',
            'pdf_robot' => $this->pdfRobotComplet ? 'complet' : 'extrait',
            'pdf_anterieur_abonnement' => $this->pdfAnterieurAbonnement ? 'ouvert' : 'ferme',
        ];
    }
}
