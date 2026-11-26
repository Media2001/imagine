<?php

declare(strict_types=1);

use Imagine\Site\ExtractionsRegles;

return [
    'titre' => 'Abonnés actifs — total et modes de paiement',
    'phrase' => 'Une ligne par abonnement dont l’état affiché est Actif dans C18 (Mon compte), pas une personne dédupliquée ni une décision d’accès ou de liste d’envoi C13. Total et répartition utilisent les mêmes lignes ; mode natif C15, vide = non renseigné, jamais déduit. Les autres états, dont la grâce, restent exclus comme dans le filtre Actif de C18.',
    'calcul' => static function (array $data): array {
        $rows = ExtractionsRegles::selectionner('etat', ['etat' => 'Actif'], $data['abonnements']);
        $out = ['total' => count($rows)];
        foreach ($rows as $row) {
            $key = 'mode:' . ($row['mode_paiement'] === '' ? 'inconnu' : $row['mode_paiement']);
            $out[$key] = ($out[$key] ?? 0) + 1;
        }
        return $out;
    },
];
