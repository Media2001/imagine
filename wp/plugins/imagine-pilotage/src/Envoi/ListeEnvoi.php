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
        usort($lignes, static fn (array $a, array $b): int =>
            strcmp($a['abonnement_id'], $b['abonnement_id'])
            ?: strcmp($a['destinataire_id'], $b['destinataire_id']));
        $anomalies = [];
        $groupes = [];
        foreach ($lignes as $index => $ligne) {
            if (
                trim($ligne['destinataire']) === '' || trim($ligne['rue']) === ''
                || trim($ligne['code_postal']) === '' || trim($ligne['ville']) === ''
            ) {
                $anomalies[] = ['motif' => 'adresse_incomplete', 'ligne' => $index, 'exemplaire' => $ligne];
            }
            if (trim($ligne['pays']) === '') {
                $anomalies[] = ['motif' => 'pays_manquant', 'ligne' => $index, 'exemplaire' => $ligne];
            }
            $cle = [];
            foreach (['destinataire', 'rue', 'complement', 'code_postal', 'ville', 'pays'] as $champ) {
                $cle[] = strtolower(preg_replace('/\s+/u', ' ', trim($ligne[$champ])));
            }
            $groupes[json_encode($cle, JSON_THROW_ON_ERROR)][] = $index;
        }
        foreach ($groupes as $indices) {
            if (count($indices) < 2) {
                continue;
            }
            foreach ($indices as $index) {
                $anomalies[] = [
                    'motif' => 'doublon_destinataire_adresse', 'ligne' => $index, 'exemplaire' => $lignes[$index],
                ];
            }
        }
        usort($anomalies, static fn (array $a, array $b): int =>
            strcmp($a['motif'], $b['motif']) ?: $a['ligne'] <=> $b['ligne']);
        return new self($numero, $cloture, $lignes, $anomalies);
    }
}
