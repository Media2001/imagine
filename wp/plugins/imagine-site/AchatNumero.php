<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;

/** Conversion pure d'une ligne native vérifiée vers le contrat achat de C06. */
final class AchatNumero
{
    /** Par ligne, un partiel non ventilé ne désigne aucune acquisition à retirer. */
    public static function remboursement(mixed $portee, bool $present, bool $complet, bool $ligne): bool
    {
        return $complet || ($present && ($portee !== 'ligne' || $ligne));
    }

    public static function droit(int $client, array $ligne): ?array
    {
        if (
            $client <= 0 || ($ligne['client'] ?? null) !== $client
            || !in_array($ligne['etat'] ?? null, ['processing', 'completed'], true)
            || ($ligne['payee'] ?? null) !== true
            || !($ligne['acquis'] ?? null) instanceof DateTimeImmutable
            || $ligne['acquis']->format('u') !== '000000'
            || ($ligne['remboursement'] ?? null) !== false
            || !is_int($ligne['instantane'] ?? null) || $ligne['instantane'] <= 0
            || ($ligne['publie'] ?? null) !== true
            || !is_numeric($ligne['quantite'] ?? null) || $ligne['quantite'] <= 0
        ) {
            return null;
        }
        return ['type' => 'achat', 'numero' => (string) $ligne['instantane'], 'acquis_le' => $ligne['acquis']];
    }
}
