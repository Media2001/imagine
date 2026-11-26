<?php

declare(strict_types=1);

use Imagine\Site\EcheancesRegles;

return [
    'titre' => 'Abonnements arrivant à échéance',
    'libelles' => [30 => 'À un mois — 30 jours', 90 => 'À trois mois — 90 jours', 180 => 'À six mois — 180 jours'],
    'phrase' => 'Nombre de lignes de la vue Échéances C15 à 30, 90 et 180 jours (ses fenêtres pour un, trois et six mois), cumulatives, pas des mois calendaires. Même règle C15 : états active, pending-cancel, on-hold ou pending, première date future entre prochain paiement et fin, bornes incluses. C18 filtre des jours UTC entiers tous états, et peut donc donner un autre nombre.',
    'calcul' => static function (array $data): array {
        $out = [];
        foreach ([30, 90, 180] as $days) {
            $out[$days] = count(EcheancesRegles::echeances($data['echeances'], $data['maintenant'], $days));
        }
        return $out;
    },
];
