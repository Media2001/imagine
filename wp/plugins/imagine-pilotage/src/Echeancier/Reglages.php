<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Echeancier;

/** Règles ouvertes C05, arbitrage du 22/11/2026. Aucun effet financier. */
final readonly class Reglages
{
    public function __construct(
        public ?int $margeJours = null,
        public string $apresRejet = 'restent_dues',
        public string $tarif = 'fige_bloc'
    ) {
        if ($margeJours !== null && $margeJours < 1) {
            throw new \InvalidArgumentException('La marge civile doit être strictement positive.');
        }
        if (!in_array($apresRejet, ['restent_dues', 'annuler_restantes'], true)) {
            throw new \InvalidArgumentException('REJET_INVALIDE');
        }
        if (!in_array($tarif, ['fige_bloc', 'courant_impayes'], true)) {
            throw new \InvalidArgumentException('TARIF_INVALIDE');
        }
    }

    /** Décode strictement la valeur persistée ou le formulaire Settings API. */
    public static function depuisOption(mixed $valeur): self
    {
        if (!is_array($valeur)) {
            throw new \InvalidArgumentException('REGLAGES_INVALIDES');
        }
        $marge = $valeur['marge_jours'] ?? null;
        if ($marge === '') {
            $marge = null;
        }
        if ($marge !== null) {
            if ((!is_int($marge) && !is_string($marge)) || !preg_match('/^[1-9][0-9]*$/D', (string) $marge)) {
                throw new \InvalidArgumentException('MARGE_INVALIDE');
            }
            $marge = filter_var($marge, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]]);
            if ($marge === false) {
                throw new \InvalidArgumentException('MARGE_INVALIDE');
            }
        }
        $rejet = $valeur['apres_rejet'] ?? 'restent_dues';
        $tarif = $valeur['tarif'] ?? 'fige_bloc';
        if (!is_string($rejet)) {
            throw new \InvalidArgumentException('REJET_INVALIDE');
        }
        if (!is_string($tarif)) {
            throw new \InvalidArgumentException('TARIF_INVALIDE');
        }
        return new self($marge, $rejet, $tarif);
    }

    /**
     * Projection seule : pas de remise, écriture Woo, accès ou prélèvement.
     * Les sommes sont des centimes par échéance, pas un tarif annuel à diviser.
     * @param list<int> $rangsPayes Confirmations reçues, sans avance du curseur sur échec.
     * @return array<int, int> Créances encore dues par rang dans le bloc courant.
     */
    public function montantsRestants(
        int $montantFigeCentimes,
        int $tarifCourantCentimes,
        array $rangsPayes,
        bool $rejet
    ): array {
        if ($montantFigeCentimes < 0 || $tarifCourantCentimes < 0) {
            throw new \InvalidArgumentException('MONTANT_INVALIDE');
        }
        foreach ($rangsPayes as $rang) {
            if (!is_int($rang) || $rang < 1 || $rang > 4) {
                throw new \InvalidArgumentException('RANG_INVALIDE');
            }
        }
        if ($rejet && $this->apresRejet === 'annuler_restantes') {
            return [];
        }
        $resultat = [];
        foreach ([1, 2, 3, 4] as $rang) {
            if (!in_array($rang, $rangsPayes, true)) {
                $resultat[$rang] = $this->tarif === 'fige_bloc' ? $montantFigeCentimes : $tarifCourantCentimes;
            }
        }
        return $resultat;
    }
}
