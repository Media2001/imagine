<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

use InvalidArgumentException;

final readonly class Calendrier
{
    /** @var list<Numero> */
    public array $numeros;

    /** @param list<Numero> $numeros */
    public function __construct(array $numeros)
    {
        $ids = [];
        foreach ($numeros as $numero) {
            if (!$numero instanceof Numero || isset($ids[$numero->id])) {
                throw new InvalidArgumentException('Numéro invalide ou identifiant en double.');
            }
            $ids[$numero->id] = true;
        }
        usort($numeros, static fn (Numero $a, Numero $b): int => $a->sortie <=> $b->sortie ?: strcmp($a->id, $b->id));
        $this->numeros = array_values($numeros);
    }
}
