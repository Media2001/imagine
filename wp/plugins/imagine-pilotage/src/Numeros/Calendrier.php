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
            foreach ($this->numeros as $fige) {
                if ($fige->type !== $ancien->type || !$fige->estCloture($date)) {
                    continue;
                }
                $avant = $ancien->sortie <=> $fige->sortie ?: strcmp($ancien->id, $fige->id);
                $apres = $nouveau->sortie <=> $fige->sortie ?: strcmp($nouveau->id, $fige->id);
                if (($avant < 0) !== ($apres < 0)) {
                    throw new \LogicException('Le déplacement changerait le rang d’un numéro déjà clôturé.');
                }
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
        $precedent = null;
        foreach ($numeros as $numero) {
            if ($numero->type !== TypeNumero::Regulier) {
                continue;
            }
            if ($precedent !== null && $numero->cloture < $precedent->cloture) {
                throw new InvalidArgumentException(
                    'Clôtures inversées : ' . $precedent->id . ' et ' . $numero->id . '.'
                );
            }
            $precedent = $numero;
        }
        $this->numeros = array_values($numeros);
    }
}
