<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

use InvalidArgumentException;

final readonly class Calendrier
{
    /** @var list<Numero> */
    public array $numeros;

    public function modifier(Numero $nouveau, \DateTimeImmutable $date): self
    {
        $numeros = $this->numeros;
        foreach ($numeros as $index => $ancien) {
            if ($ancien->id !== $nouveau->id) {
                continue;
            }
            if ($ancien->estCloture($date) || $nouveau->estCloture($date)) {
                throw new \LogicException('Une clôture passée ou rétroactive ne peut être modifiée.');
            }
            if ($ancien->type !== $nouveau->type) {
                throw new InvalidArgumentException('Le type d’un numéro ne peut pas changer.');
            }
            $numeros[$index] = $nouveau;
            return new self($numeros);
        }
        throw new \OutOfBoundsException('Numéro absent du calendrier.');
    }

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
