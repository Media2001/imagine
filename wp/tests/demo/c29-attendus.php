<?php

declare(strict_types=1);

// Attendu indépendant du calcul C29, des statuts d'accès C06 et de l'adaptateur.
// [statut ou absence, tarif, coopérateur, raison]. Tous choisissent principale sauf les absents/retrait.
return [
    'V-DEC' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'V-DEC-FIN' => ['a_retirer', null, null, 'desinscrit_de_tout'],
    'V-INSCRIT' => [null, null, null, 'aucun_choix_lecteur'],
    'A-CARTE' => ['abonne', 'normal-1', 'non', 'eligible'],
    'A-SEPA4' => ['abonne', 'normal-4', 'non', 'eligible'],
    'A-PAYPAL' => ['abonne', 'normal-1', 'non', 'eligible'],
    'A-VIR' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'A-PAPIER' => ['abonne', 'normal-4', 'non', 'eligible'],
    'A-GRACE' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'A-SUSP' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'A-EXPIRE' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'A-NONRENOUV' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'A-ETRANGER' => ['abonne', 'inconnu', 'non', 'eligible'],
    'A-SANSMAIL' => [null, null, null, 'email_non_recevable'],
    'A-ECHEANCE' => ['abonne', 'inconnu', 'non', 'eligible'],
    'P-OFFRANT' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'P-OFFERT' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'P-GEST' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'P-BENEF' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'P-PRO' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'P-SOL-ATT' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'P-SOL-OK' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'P-NUMERO' => ['non_abonne', 'inconnu', 'non', 'eligible'],
    'P-COOP' => ['non_abonne', 'inconnu', 'oui', 'eligible'],
    'E-ADMIN' => [null, null, null, 'aucun_choix_lecteur'],
    'E-REDAC' => [null, null, null, 'aucun_choix_lecteur'],
    'E-ABO' => [null, null, null, 'aucun_choix_lecteur'],
];
