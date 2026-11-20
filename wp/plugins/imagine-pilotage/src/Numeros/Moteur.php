<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

use DateTimeImmutable;

final readonly class Moteur
{
    public function __construct(public Calendrier $calendrier)
    {
    }

    public function ouvrir(DateTimeImmutable $commande): Annee
    {
        return new Annee($commande);
    }

    public function accesNumerique(Annee $annee, DateTimeImmutable $date): bool
    {
        return $annee->estActive($date) && $date < $annee->finNumerique();
    }

    /** @return list<Echeance> Dates théoriques seulement, aucun prélèvement exécuté. */
    public function echeances(Annee $annee, int $margeJours): array
    {
        if ($margeJours < 1) {
            throw new \InvalidArgumentException('La marge avant clôture doit être strictement positive.');
        }
        return array_map(
            static fn (Numero $numero): Echeance => new Echeance(
                $numero,
                $numero->cloture->sub(new \DateInterval('P' . $margeJours . 'D'))
            ),
            $this->numeros($annee)
        );
    }

    /** @return list<Numero> Numéros éligibles non encore sortis, hors-série compris. */
    public function restants(Annee $annee, DateTimeImmutable $date): array
    {
        return array_values(array_filter(
            $this->calendrier->numeros,
            fn (Numero $numero): bool => $numero->sortie > $date && $this->aDroit($annee, $numero->id, $date)
        ));
    }

    public function aDroit(Annee $annee, string $id, DateTimeImmutable $date): bool
    {
        $numeros = $this->numeros($annee);
        $horsSerie = $this->horsSerie($annee);
        if ($horsSerie !== null) {
            $numeros[] = $horsSerie;
        }
        foreach ($numeros as $numero) {
            if ($numero->id === $id) {
                // Après clôture : état historique, jamais l'état courant réactivé.
                $reference = $numero->estCloture($date) ? $numero->cloture : $date;
                return $annee->estActive($reference);
            }
        }
        return false;
    }

    public function renouveler(Annee $precedente, DateTimeImmutable $debut): Annee
    {
        if ($debut <= $precedente->debut) {
            throw new \InvalidArgumentException('Le renouvellement doit suivre le début précédent.');
        }
        return new Annee($debut, $precedente);
    }

    public function nonResolus(Annee $annee): int
    {
        return 4 - count($this->numeros($annee));
    }

    /** @return list<Numero> */
    public function numeros(Annee $annee): array
    {
        if ($annee->precedente !== null) {
            $dernier = $this->dernier($annee->precedente);
            if ($dernier === null) {
                return [];
            }
            $reguliers = array_values(array_filter(
                $this->calendrier->numeros,
                static fn (Numero $numero): bool => $numero->type === TypeNumero::Regulier
            ));
            foreach ($reguliers as $index => $numero) {
                if ($numero->id === $dernier->id) {
                    return array_slice($reguliers, $index + 1, 4);
                }
            }
            return [];
        }
        $ouverts = array_filter(
            $this->calendrier->numeros,
            static fn (Numero $numero): bool => $numero->type === TypeNumero::Regulier
                && !$numero->estCloture($annee->debut)
        );
        return array_slice(array_values($ouverts), 0, 4);
    }

    public function premier(Annee $annee): ?Numero
    {
        return $this->numeros($annee)[0] ?? null;
    }

    public function dernier(Annee $annee): ?Numero
    {
        $numeros = $this->numeros($annee);
        return count($numeros) === 4 ? $numeros[3] : null;
    }

    public function horsSerie(Annee $annee): ?Numero
    {
        foreach ($this->calendrier->numeros as $numero) {
            if ($numero->type === TypeNumero::HorsSerie && !$numero->estCloture($annee->debut)) {
                return $numero;
            }
        }
        return null;
    }
}
