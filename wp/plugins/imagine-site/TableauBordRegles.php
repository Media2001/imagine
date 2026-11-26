<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Catalogue pur : un fichier associe le calcul et l'explication d'un indicateur. */
final class TableauBordRegles
{
    public static function catalogue(): array
    {
        static $out = null;
        if ($out !== null) {
            return $out;
        }
        $out = [];
        foreach (glob(__DIR__ . '/indicateurs/*.php') as $path) {
            $out[basename($path, '.php')] = require $path;
        }
        return $out;
    }

    public static function calculer(string $id, array $data): array
    {
        $definition = self::catalogue()[$id] ?? null;
        if (!$definition) {
            throw new \InvalidArgumentException('Indicateur indisponible.');
        }
        $values = ($definition['calcul'])($data);
        $labels = $definition['libelles'] ?? [];
        return ['titre' => $definition['titre'], 'phrase' => $definition['phrase'],
            'valeurs' => $values, 'libelles' => is_callable($labels) ? $labels($values) : $labels];
    }
}
