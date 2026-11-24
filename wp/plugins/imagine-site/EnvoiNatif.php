<?php

declare(strict_types=1);
namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\{Calendrier, Numero, TypeNumero};

/** Raccord WordPress : aucune règle de sélection de C01/C07 recopiée. */
final class EnvoiNatif
{
    public static function calendrier(): Calendrier
    {
        $numeros = [];
        $zone = new DateTimeZone('Europe/Brussels');
        foreach (get_option('imagine_demo_calendrier', []) as $row) {
            foreach (['sortie', 'cloture'] as $key) {
                if (!NumeroPublication::valid($row[$key] ?? null)) {
                    throw new \RuntimeException('Calendrier postal invalide.');
                }
            }
            $numeros[] = new Numero($row['code'], TypeNumero::from($row['type']),
                new DateTimeImmutable($row['sortie'], $zone), new DateTimeImmutable($row['cloture'], $zone));
        }
        return new Calendrier($numeros);
    }
}
