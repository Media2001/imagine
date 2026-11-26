<?php

declare(strict_types=1);

use Imagine\Site\EcheancesRegles;

return [
    'titre' => 'Paiements échoués en cours',
    'phrase' => 'Nombre de commandes natives liées à un abonnement du même titulaire, parent ou renouvellement, dans la vue Paiements échoués C15 : statut failed, non payées et sans date de paiement. Une commande compte une fois, pas un abonné ; aucun échec bancaire ni retard n’est déduit.',
    'calcul' => static fn (array $data): array => ['total' => count(EcheancesRegles::paiements($data['echecs'], 'echecs'))],
];
