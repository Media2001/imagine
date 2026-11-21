<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Echeancier;

use DateTimeImmutable;
use Imagine\Pilotage\Numeros\Annee;
use Imagine\Pilotage\Numeros\Moteur;

/** Proposition pure : aucune commande, somme ou autorisation financière. */
final readonly class Planificateur
{
    public function __construct(private Moteur $numeros)
    {
    }

    /** @return list<Versement> */
    public function planifier(Annee $annee, DateTimeImmutable $finEngagement, int $margeJours): array
    {
        if ($finEngagement <= $annee->debut) {
            throw new \InvalidArgumentException('FIN_ENGAGEMENT doit suivre le début.');
        }
        $echeances = $this->numeros->echeances($annee, $margeJours);
        if (count($echeances) !== 4) {
            throw new \DomainException('CALENDRIER_INCOMPLET : quatre numéros C01 requis.');
        }
        $resultat = [];
        $precedente = null;
        foreach ($echeances as $index => $echeance) {
            $initial = $index === 0 && $annee->precedente === null;
            $date = $initial ? $annee->debut : $echeance->lancement;
            if ($date < $annee->debut || $date >= $finEngagement) {
                throw new \DomainException(
                    'HORS_ENGAGEMENT ' . $echeance->numero->id . ' ' . $date->format(DATE_ATOM)
                );
            }
            if ($precedente !== null && $date <= $precedente) {
                throw new \DomainException('DATES_NON_CROISSANTES ' . $echeance->numero->id);
            }
            $precedente = $date;
            $resultat[] = new Versement(
                $index + 1,
                $echeance->numero,
                $date,
                $initial
            );
        }
        return $resultat;
    }
}
