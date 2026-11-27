<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Décision sans WordPress : une déclaration n'est jamais un signal de navigation. */
final class AcquisitionRegles
{
    public static function liste(mixed $value): ?array
    {
        if (!is_array($value) || count($value) > 20) {
            return null;
        }
        foreach ($value as $key => $label) {
            if (!is_string($key) || !preg_match('/^[a-z][a-z0-9_-]{0,39}$/D', $key)
                || !is_string($label) || trim($label) !== $label || $label === ''
                || mb_strlen($label, 'UTF-8') > 80 || preg_match('/[<>\x00-\x1f\x7f]/u', $label)) {
                return null;
            }
        }
        return $value;
    }

    public static function jour(string $value): bool
    {
        $date = \DateTimeImmutable::createFromFormat('!Y-m-d', $value, new \DateTimeZone('UTC'));
        return $date !== false && $date->format('Y-m-d') === $value;
    }

    /** Agrégats de déclarations, jamais des personnes ; bornes civiles UTC inclusives. */
    public static function compter(array $rows, string $from, string $until): ?array
    {
        if (!self::jour($from) || !self::jour($until) || $from > $until) {
            return null;
        }
        $out = [];
        foreach ($rows as $row) {
            if (($row['etat'] ?? '') === 'effacee') {
                continue;
            }
            if (!isset($row['date'], $row['choix'], $row['libelle']) || !is_string($row['date'])
                || !preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/D', $row['date'])
                || !self::jour(substr($row['date'], 0, 10))
                || self::liste([$row['choix'] => $row['libelle']]) === null) {
                throw new \RuntimeException('Déclaration illisible');
            }
            if ($row['date'] < $from . 'T00:00:00Z' || $row['date'] > $until . 'T23:59:59Z') {
                continue;
            }
            $key = $row['choix'] . ':' . $row['libelle'];
            $out[$key] ??= ['choix' => $row['choix'], 'libelle' => $row['libelle'], 'nombre' => 0];
            ++$out[$key]['nombre'];
        }
        ksort($out);
        return array_values($out);
    }

    public static function eligible(int $actor, int $owner, bool $paid, bool $dated, string $via): bool
    {
        return $actor > 0 && $actor === $owner && $paid && $dated && $via !== 'imagine-c16';
    }
}
