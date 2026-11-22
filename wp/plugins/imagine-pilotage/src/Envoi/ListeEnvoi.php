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
        DateTimeImmutable $cloture,
        bool $inclureGrace = true
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
        $anomalies = [];
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
                $situation === null
                || ($situation->fin !== null && $situation->fin <= $cloture)
                || !(
                    ($situation->etat === 'actif' && $situation->paiementValide)
                    || ($situation->etat === 'grace' && $inclureGrace)
                )
                || !in_array($numero->id, $situation->numerosDus, true)
            ) {
                continue;
            }
            if ($situation->destinataires === [] && $abonnement->origine !== 'groupe') {
                $anomalies[] = ['motif' => 'destinataire_manquant', 'abonnement_id' => $abonnement->id];
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
        $groupes = [];
        foreach ($lignes as $index => $ligne) {
            if (
                self::normaliserEspaces($ligne['destinataire']) === ''
                || self::normaliserEspaces($ligne['rue']) === ''
                || self::normaliserEspaces($ligne['code_postal']) === ''
                || self::normaliserEspaces($ligne['ville']) === ''
            ) {
                $anomalies[] = ['motif' => 'adresse_incomplete', 'ligne' => $index, 'exemplaire' => $ligne];
            }
            if (self::normaliserEspaces($ligne['pays']) === '') {
                $anomalies[] = ['motif' => 'pays_manquant', 'ligne' => $index, 'exemplaire' => $ligne];
            }
            $cle = [];
            foreach (['destinataire', 'rue', 'complement', 'code_postal', 'ville', 'pays'] as $champ) {
                $cle[] = mb_strtolower(self::normaliserEspaces($ligne[$champ]), 'UTF-8');
            }
            $groupes[json_encode(['nom', $cle], JSON_THROW_ON_ERROR)][] = $index;
            if ($ligne['destinataire_id'] !== '') {
                $identite = ['id', $ligne['destinataire_id'], array_slice($cle, 1)];
                $groupes[json_encode($identite, JSON_THROW_ON_ERROR)][] = $index;
            }
        }
        $doublons = [];
        foreach ($groupes as $indices) {
            if (count($indices) < 2) {
                continue;
            }
            foreach ($indices as $index) {
                $doublons[$index] = true;
            }
        }
        foreach (array_keys($doublons) as $index) {
            $anomalies[] = [
                'motif' => 'doublon_destinataire_adresse', 'ligne' => $index, 'exemplaire' => $lignes[$index],
            ];
        }
        usort($anomalies, static fn (array $a, array $b): int =>
            strcmp($a['motif'], $b['motif'])
            ?: ($a['ligne'] ?? -1) <=> ($b['ligne'] ?? -1)
            ?: strcmp($a['abonnement_id'] ?? '', $b['abonnement_id'] ?? ''));
        return new self($numero, $cloture, $lignes, $anomalies);
    }

    private static function normaliserEspaces(string $valeur): string
    {
        return trim(preg_replace('/[\s\p{Z}]+/u', ' ', $valeur));
    }
}
