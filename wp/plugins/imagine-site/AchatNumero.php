<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;

/** Conversion pure d'une ligne native vérifiée vers le contrat achat de C06. */
final class AchatNumero
{
    public static function droit(int $client, array $ligne): ?array
    {
        if (
            $client <= 0 || ($ligne['client'] ?? null) !== $client
            || !in_array($ligne['etat'] ?? null, ['processing', 'completed'], true)
            || ($ligne['payee'] ?? null) !== true
            || !($ligne['acquis'] ?? null) instanceof DateTimeImmutable
            || $ligne['acquis']->format('u') !== '000000'
            || ($ligne['remboursement'] ?? null) !== false
            || !is_int($ligne['numero'] ?? null) || $ligne['numero'] <= 0
            || ($ligne['instantane'] ?? null) !== $ligne['numero']
            || !is_numeric($ligne['quantite'] ?? null) || $ligne['quantite'] <= 0
        ) {
            return null;
        }
        return ['type' => 'achat', 'numero' => (string) $ligne['numero'], 'acquis_le' => $ligne['acquis']];
    }
}
