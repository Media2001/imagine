<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Catalogue de fichiers : colonnes, filtres, requête et prédicat d'une extraction ensemble. */
final class ExtractionsRegles
{
    public const COLONNES = ['abonnement_id', 'compte_id', 'prenom', 'nom', 'email', 'destinataire',
        'rue', 'complement', 'code_postal', 'ville', 'pays', 'formule', 'mode_paiement', 'etat', 'echeance_utc'];

    public static function catalogue(): array
    {
        $out = [];
        foreach (glob(__DIR__ . '/extractions/*.php') as $path) {
            $out[basename($path, '.php')] = require $path;
        }
        return $out;
    }

    public static function definition(string $id): array
    {
        $definition = self::catalogue()[$id] ?? null;
        if (!$definition || !($definition['disponible'] ?? false)) {
            throw new \InvalidArgumentException('Extraction indisponible.');
        }
        return $definition;
    }

    public static function filtres(string $id, array $request): array
    {
        $out = [];
        foreach (self::definition($id)['filtres'] as $key => $spec) {
            $value = $request[$key] ?? '';
            if (!is_string($value) || strlen($value) > 80 || preg_match('/[\x00-\x1f\x7f]/', $value)) {
                throw new \InvalidArgumentException('Filtre invalide.');
            }
            $value = trim($value);
            if (isset($spec['options']) && !array_key_exists($value, $spec['options'])) {
                throw new \InvalidArgumentException('Choix invalide.');
            }
            if (isset($spec['pattern']) && !preg_match($spec['pattern'], $value)) {
                throw new \InvalidArgumentException('Format invalide.');
            }
            if ($spec['type'] === 'date') {
                $date = \DateTimeImmutable::createFromFormat('!Y-m-d', $value, new \DateTimeZone('UTC'));
                if (!$date || $date->format('Y-m-d') !== $value) {
                    throw new \InvalidArgumentException('Date invalide.');
                }
            }
            $out[$key] = $value;
        }
        if (!(self::definition($id)['validation'] ?? static fn (): bool => true)($out)) {
            throw new \InvalidArgumentException('Période inversée.');
        }
        return $out;
    }

    public static function selectionner(string $id, array $filters, array $rows): array
    {
        $definition = self::definition($id);
        $filters = self::filtres($id, $filters);
        return array_values(array_filter($rows, static fn (array $row): bool => ($definition['selection'])($row, $filters)));
    }
}
