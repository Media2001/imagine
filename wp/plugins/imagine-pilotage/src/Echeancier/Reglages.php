<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Echeancier;

/** Règles ouvertes C05, arbitrage du 22/11/2026. Aucun effet financier. */
final readonly class Reglages
{
    public function __construct(
        public ?int $margeJours = null,
        public string $apresRejet = 'restent_dues',
        public string $tarif = 'fige_bloc',
        public string $confirmationPremierSepa = 'avec_marge'
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
        if (!in_array($confirmationPremierSepa, ['avec_marge', 'sans_marge'], true)) {
            throw new \InvalidArgumentException('CONFIRMATION_PREMIER_SEPA_INVALIDE');
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
        $sepa = array_key_exists('confirmation_premier_sepa', $valeur)
            ? $valeur['confirmation_premier_sepa'] : 'avec_marge';
        if (!is_string($sepa)) {
            throw new \InvalidArgumentException('CONFIRMATION_PREMIER_SEPA_INVALIDE');
        }
        return new self($marge, $rejet, $tarif, $sepa);
    }

    /**
     * Premier paiement SEPA seulement : projection, jamais une confirmation bancaire.
     * Avec marge : max(confirmation effective, commande + marge civile Europe/Brussels).
     * Sans marge : confirmation effective. Null signifie absence de confirmation.
     * Ne modifie ni le numéro C01, ni les dates de lancement, ni Woo, ni les droits.
     */
    public function premierSepaPayeLe(
        \DateTimeImmutable $commande,
        ?\DateTimeImmutable $confirmation
    ): ?\DateTimeImmutable {
        if ($this->confirmationPremierSepa === 'avec_marge' && $this->margeJours === null) {
            throw new \InvalidArgumentException('MARGE_OBLIGATOIRE : renseigner les jours civils avant confirmation.');
        }
        if ($confirmation === null) {
            return null;
        }
        if ($confirmation < $commande) {
            throw new \InvalidArgumentException('CONFIRMATION_ANTERIEURE_COMMANDE');
        }
        $confirmation = $confirmation->setTimezone(new \DateTimeZone('Europe/Brussels'));
        if ($this->confirmationPremierSepa === 'sans_marge') {
            return $confirmation;
        }
        $disponible = $commande->setTimezone(new \DateTimeZone('Europe/Brussels'))
            ->add(new \DateInterval('P' . $this->margeJours . 'D'));
        return $confirmation > $disponible ? $confirmation : $disponible;
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
