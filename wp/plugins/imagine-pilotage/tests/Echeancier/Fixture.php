<?php

declare(strict_types=1);

use Imagine\Pilotage\Echeancier\Planificateur;
use Imagine\Pilotage\Echeancier\Reglages;
use Imagine\Pilotage\Numeros\Activation;
use Imagine\Pilotage\Numeros\Annee;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Numeros\Numero;
use Imagine\Pilotage\Numeros\TypeNumero;

function c05Date(string $date): DateTimeImmutable
{
    return new DateTimeImmutable($date, new DateTimeZone('Europe/Brussels'));
}

function c05Calendrier(): Calendrier
{
    $numeros = [];
    foreach (range(2026, 2031) as $year) {
        foreach ([1, 4, 7, 10] as $month) {
            $id = sprintf('REG-%d-%02d', $year, $month);
            $numeros[] = new Numero(
                $id,
                TypeNumero::Regulier,
                c05Date(sprintf('%d-%02d-20', $year, $month)),
                c05Date(sprintf('%d-%02d-10', $year, $month))
            );
        }
        $numeros[] = new Numero(
            'HS-' . $year,
            TypeNumero::HorsSerie,
            c05Date($year . '-08-20'),
            c05Date($year . '-08-10')
        );
    }
    return new Calendrier($numeros);
}

function c05Annee(string $date): Annee
{
    return (new Annee(c05Date($date)))->activer(c05Date($date), Activation::Paiement);
}


/** Contre-exemple de fusion : calendrier C01 autorisé, jonction C05 égale. */
function c05CalendrierJonctionEgale(): Calendrier
{
    $numeros = c05Calendrier()->numeros;
    $cloture = c05Date('2028-01-10');
    foreach ($numeros as $index => $numero) {
        if ($numero->id === 'REG-2028-04') {
            $numeros[$index] = new Numero($numero->id, $numero->type, $numero->sortie, $cloture);
        }
    }
    return new Calendrier($numeros);
}
