<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Echeancier;

/** Doubles de contrat : le parcours WordPress réel est exercé dans le banc e2e. */
final class WordPressFictif
{
    public static array $appels = [];
}
