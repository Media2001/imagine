<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Envoi;

use DateTimeImmutable;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Numero;

final readonly class ListeEnvoi
{
    private function __construct(
        public Numero $numero,
        public DateTimeImmutable $cloture,
        public array $lignes,
        public array $anomalies
    ) {
    }

    /** @param list<Abonnement> $abonnements */
    public static function etablir(
        Numero $numero,
        Calendrier $calendrier,
        array $abonnements,
        DateTimeImmutable $cloture
    ): self {
        $reference = array_values(array_filter(
            $calendrier->numeros,
            static fn (Numero $n): bool => $n->id === $numero->id
        ));
        if ($reference === [] || $reference[0] != $numero || $cloture != $numero->cloture) {
            throw new \InvalidArgumentException('Numéro ou clôture incohérent avec le calendrier.');
        }
        $ids = [];
        foreach ($abonnements as $abonnement) {
            if (isset($ids[$abonnement->id])) {
                throw new \InvalidArgumentException('Abonnement en double dans les entrées.');
            }
            $ids[$abonnement->id] = true;
        }
        $lignes = [];
        foreach ($abonnements as $abonnement) {
            if ($abonnement->creation >= $cloture || $abonnement->origine === 'numero_unite') {
                continue;
            }
            $historique = array_values(array_filter(
                $abonnement->situations,
                static fn (Situation $s): bool => $s->effet < $cloture && $s->enregistre < $cloture
            ));
            usort($historique, static fn (Situation $a, Situation $b): int => $a->effet <=> $b->effet);
            $situation = $historique === [] ? null : $historique[array_key_last($historique)];
            if (
                $situation === null || !$situation->paiementValide
                || ($situation->fin !== null && $situation->fin <= $cloture)
                || !in_array($situation->etat, ['actif', 'grace'], true)
                || !in_array($numero->id, $situation->numerosDus, true)
            ) {
                continue;
            }
            foreach ($situation->destinataires as $destinataire) {
                $lignes[] = [
                    'abonnement_id' => $abonnement->id,
                    'destinataire_id' => $destinataire->id,
                    'destinataire' => $destinataire->nom,
                    'rue' => $destinataire->rue,
                    'complement' => $destinataire->complement,
                    'code_postal' => $destinataire->codePostal,
                    'ville' => $destinataire->ville,
                    'pays' => $destinataire->pays,
                    'origine' => $abonnement->origine,
                ];
            }
        }
        return new self($numero, $cloture, $lignes, []);
    }
}
