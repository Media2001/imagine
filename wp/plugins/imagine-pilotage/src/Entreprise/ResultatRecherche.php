<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Entreprise;

use InvalidArgumentException;

/** Null signifie indisponible, jamais « entreprise inexistante ». */
final readonly class ResultatRecherche
{
    public function __construct(public ?string $denomination = null)
    {
        if ($denomination !== null && preg_match('/\A[\s\p{Zs}]*\z/u', $denomination) !== 0) {
            throw new InvalidArgumentException('La dénomination fournie doit contenir du texte UTF-8.');
        }
    }

    public function estDisponible(): bool
    {
        return $this->denomination !== null;
    }

    public function message(?callable $traduire = null): string
    {
        $texte = $this->estDisponible()
            ? 'Une dénomination a été trouvée.'
            : 'La recherche de dénomination n’est pas disponible.';
        return $traduire === null ? $texte : $traduire($texte);
    }
}
