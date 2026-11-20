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
        return new self($saisie);
    }

    public function estValide(): bool
    {
        return $this->motif === null;
    }

    public function affichage(): ?string
    {
        return substr($this->normalise, 0, 4) . '.'
            . substr($this->normalise, 4, 3) . '.' . substr($this->normalise, 7);
    }

    public function message(): string
    {
        return 'Le numéro d’entreprise est cohérent.';
    }
}
