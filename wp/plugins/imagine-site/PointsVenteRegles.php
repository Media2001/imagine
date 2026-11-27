<?php

declare(strict_types=1);

namespace Imagine\Site;

use InvalidArgumentException;

/** CSV pur : aucun fichier persistant, aucune connaissance de WordPress. */
final class PointsVenteRegles
{
    public const REQUIS = ['nom', 'adresse', 'localite', 'postal'];
    public const FACULTATIFS = ['personne', 'telephone'];

    public static function cle(string $value): string
    {
        $value = mb_strtolower(trim($value), 'UTF-8');
        $value = strtr($value, array_combine(
            preg_split('//u', 'àáâãäåāăąçćčďđèéêëēĕėęěìíîïĩīĭįıñńňòóôõöøōŏőŕřśşšťùúûüũūŭůűųýÿžźż', -1, PREG_SPLIT_NO_EMPTY),
            str_split('aaaaaaaaacccddeeeeeeeeeiiiiiiiiinnnooooooooorrssstuuuuuuuuuuyyzzz')
        ));
        return preg_replace('/\\p{M}+/u', '', $value);
    }

    public static function rechercher(array $rows, string $query): array
    {
        $key = self::cle($query);
        $result = array_values(array_filter($rows, static fn (array $row): bool => $key === ''
            || self::cle($row['localite']) === $key || self::cle($row['postal']) === $key));
        usort($result, static fn (array $a, array $b): int => [self::cle($a['localite']), self::cle($a['nom']), $a['postal'], $a['adresse']]
            <=> [self::cle($b['localite']), self::cle($b['nom']), $b['postal'], $b['adresse']]);
        return $result;
    }

    public static function mapping(array $mapping): array
    {
        if (array_diff(self::REQUIS, array_keys($mapping)) !== []
            || array_diff(array_keys($mapping), [...self::REQUIS, ...self::FACULTATIFS]) !== []
        ) {
            throw new InvalidArgumentException('mapping_invalide');
        }
        foreach ($mapping as $column) {
            if (!is_string($column) || trim($column) === '' || mb_strlen($column) > 100) {
                throw new InvalidArgumentException('mapping_invalide');
            }
        }
        if (count(array_unique($mapping)) !== count($mapping)) {
            throw new InvalidArgumentException('mapping_invalide');
        }
        return $mapping;
    }

    public static function charger(string $csv, array $mapping, string $separateur): array
    {
        self::mapping($mapping);
        if (!in_array($separateur, [';', ',', "\t"], true) || strlen($csv) > 2097152
            || !mb_check_encoding($csv, 'UTF-8') || str_contains($csv, "\0")
        ) {
            throw new InvalidArgumentException('fichier_invalide');
        }
        $csv = preg_replace('/^\xEF\xBB\xBF/', '', $csv);
        $stream = fopen('php://temp', 'r+');
        fwrite($stream, $csv);
        rewind($stream);
        $header = fgetcsv($stream, null, $separateur, '"', '');
        if (!$header || count(array_unique($header)) !== count($header)
            || array_diff(array_values($mapping), $header) !== []
        ) {
            fclose($stream);
            throw new InvalidArgumentException('entete_invalide');
        }
        $cell = '(?:[^"' . preg_quote($separateur, '~') . '\r\n]*|"(?:[^"]|"")*")';
        $grammar = '~\A' . $cell . '(?:' . preg_quote($separateur, '~') . $cell . ')*\r?\n?\z~s';
        $position = ftell($stream);
        if (!preg_match($grammar, substr($csv, 0, $position))) {
            fclose($stream);
            throw new InvalidArgumentException('entete_invalide');
        }
        $line = substr_count(substr($csv, 0, $position), "\n") + 1;
        $rows = $refus = $seen = [];
        while (($values = fgetcsv($stream, null, $separateur, '"', '')) !== false) {
            $end = ftell($stream);
            $record = substr($csv, $position, $end - $position);
            $number = $line;
            $line += substr_count($record, "\n");
            $position = $end;
            $reason = !preg_match($grammar, $record) ? 'syntaxe_csv' : (count($values) !== count($header) ? 'nombre_colonnes' : '');
            $row = [];
            if ($reason === '') {
                foreach ($mapping as $field => $column) {
                    $value = trim((string) $values[array_search($column, $header, true)]);
                    if (mb_strlen($value) > 500 || preg_match('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', $value)) {
                        $reason = 'champ_invalide';
                    }
                    if (in_array($field, self::REQUIS, true) && $value === '') {
                        $reason = 'champ_requis';
                    }
                    $row[$field] = $value;
                }
            }
            $key = hash('sha256', serialize($row));
            if ($reason === '' && isset($seen[$key])) {
                $reason = 'doublon';
            }
            if ($reason !== '') {
                $refus[] = ['ligne' => $number, 'motif' => $reason];
            } else {
                $rows[] = $row;
                $seen[$key] = true;
            }
            if (count($rows) > 2000) {
                fclose($stream);
                throw new InvalidArgumentException('fichier_trop_long');
            }
        }
        fclose($stream);
        return ['lignes' => $rows, 'refus' => $refus];
    }
}
