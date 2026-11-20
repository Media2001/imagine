<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Entreprise;

/** §3.4 : résultat local immuable, sans preuve d'existence ou d'assujettissement TVA. */
final readonly class NumeroEntreprise
{
    private function __construct(public ?string $normalise, public ?Motif $motif = null)
    {
    }

    public static function depuisSaisie(string $saisie): self
    {
        // Préfixe contigu uniquement ; les autres lettres ne sont jamais effacées.
        $saisie = preg_replace('/\A\p{Zs}+|\p{Zs}+\z/u', '', $saisie);
        if ($saisie === null) {
            return new self(null, Motif::CaracteresInterdits);
        }
        $saisie = preg_replace('/\ABE/i', '', $saisie);
        if (preg_match('/\A[0-9.\-\p{Zs}]*\z/u', $saisie) !== 1) {
            return new self(null, Motif::CaracteresInterdits);
        }
        $compacte = preg_replace('/[.\-\p{Zs}]/u', '', $saisie);
        if ($compacte === '') {
            return new self(null, Motif::Vide);
        }
        if (strlen($compacte) === 9) {
            $compacte = '0' . $compacte;
        }
        if (strlen($compacte) !== 10) {
            return new self(null, Motif::Longueur);
        }
        if ($compacte[0] !== '0' && $compacte[0] !== '1') {
            return new self(null, Motif::PremierChiffre);
        }
        $cle = 97 - ((int) substr($compacte, 0, 8) % 97);
        if ((int) substr($compacte, 8, 2) !== $cle) {
            return new self(null, Motif::CleIncorrecte);
        }
        return new self($compacte);
    }

    public function estValide(): bool
    {
        return $this->motif === null;
    }

    public function affichage(): ?string
    {
        if (!$this->estValide()) {
            return null;
        }
        return substr($this->normalise, 0, 4) . '.'
            . substr($this->normalise, 4, 3) . '.' . substr($this->normalise, 7);
    }

    /** Le futur adaptateur peut injecter fn ($texte) => __($texte, 'imagine-pilotage'). */
    public function message(?callable $traduire = null): string
    {
        $texte = $this->motif?->message() ?? 'Le numéro d’entreprise est cohérent.';
        return $traduire === null ? $texte : $traduire($texte);
    }
}
