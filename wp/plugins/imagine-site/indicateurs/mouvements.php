<?php

declare(strict_types=1);

return [
    'titre' => 'Entrées et sorties du mois civil UTC — dates natives',
    'phrase' => 'Du premier jour du mois civil UTC à maintenant inclus : entrées = lignes dont la date de création native est dans la période, tous états, y compris en attente ; sorties = lignes terminées (cancelled ou expired) dont la fin native est dans la période. Dates absentes et fins futures exclues. Ce relevé des dates n’est ni une preuve de paiement ni un historique des activations, réactivations ou suspensions ; C18 n’extrait pas ces dates. Aucun taux de rétention ni motif n’en est déduit.',
    'calcul' => static function (array $data): array {
        $now = $data['maintenant'];
        $start = (new DateTimeImmutable('@' . $now))->modify('first day of this month')->setTime(0, 0)->getTimestamp();
        $inside = static fn (int $date): bool => $date > 0 && $date >= $start && $date <= $now;
        return [
            'entrees' => count(array_filter($data['mouvements'], static fn (array $row): bool => $inside($row['creation']))),
            'sorties' => count(array_filter($data['mouvements'], static fn (array $row): bool =>
                in_array($row['etat'], ['cancelled', 'expired'], true) && $inside($row['fin']))),
        ];
    },
];
