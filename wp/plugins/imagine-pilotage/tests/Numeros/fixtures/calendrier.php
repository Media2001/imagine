<?php

declare(strict_types=1);

use Imagine\Pilotage\Numeros\Numero;
use Imagine\Pilotage\Numeros\TypeNumero;

// Fiction : sorties le 5 du trimestre, clôtures le 20 du mois précédent.
// Numérotation réelle, dates inventées ; aucune donnée d'abonné.
$numeros = [];
$id = 166;
for ($annee = 2025; $annee <= 2028; $annee++) {
    foreach ([1, 4, 7, 10] as $mois) {
        if ($annee === 2025 && $mois < 10) {
            continue;
        }
        $sortie = new DateTimeImmutable(sprintf('%d-%02d-05', $annee, $mois), new DateTimeZone('Europe/Brussels'));
        $numeros[] = new Numero(
            (string) $id++,
            TypeNumero::Regulier,
            $sortie,
            $sortie->setDate(
                (int) $sortie->modify('-1 month')->format('Y'),
                (int) $sortie->modify('-1 month')->format('m'),
                20
            )
        );
    }
    $numeros[] = new Numero(
        'HS-' . $annee,
        TypeNumero::HorsSerie,
        new DateTimeImmutable($annee . '-07-15', new DateTimeZone('Europe/Brussels')),
        new DateTimeImmutable($annee . '-06-25', new DateTimeZone('Europe/Brussels'))
    );
}
return $numeros;
