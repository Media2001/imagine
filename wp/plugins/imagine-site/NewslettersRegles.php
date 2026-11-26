<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Catalogue et transitions uniquement ; aucun transport ni consentement inféré. */
final class NewslettersRegles
{
    public static function choisir(array $catalogue, array $old, array $selected, string $now, string $origin): array
    {
        self::catalogue($catalogue);
        if (array_diff($selected, array_column($catalogue, 'id'))
            || !in_array($origin, ['lecteur', 'defaut_creation'], true)
            || !preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/D', $now)) {
            throw new \InvalidArgumentException('Choix invalide.');
        }
        foreach ($catalogue as $row) {
            $id = $row['id'];
            $choice = in_array($id, $selected, true);
            if (!isset($old[$id]) || $old[$id]['choix'] !== $choice) {
                $old[$id] = ['choix' => $choice, 'date_utc' => $now, 'origine' => $origin];
            }
        }
        // Les anciennes entrées retirées du catalogue restent exportables, sans réactivation.
        return $old;
    }

    public static function catalogue(mixed $rows): array
    {
        if (!is_array($rows) || !array_is_list($rows) || count($rows) > 50) {
            throw new \InvalidArgumentException('Catalogue invalide.');
        }
        $ids = [];
        $main = 0;
        foreach ($rows as $row) {
            if (!is_array($row) || count($row) !== 4
                || !is_string($row['id'] ?? null) || !preg_match('/^[a-z][a-z0-9_-]{0,49}$/D', $row['id'])
                || isset($ids[$row['id']]) || !is_string($row['titre'] ?? null)
                || !is_string($row['presentation'] ?? null) || !is_bool($row['principale'] ?? null)) {
                throw new \InvalidArgumentException('Newsletter invalide.');
            }
            foreach (['titre' => 150, 'presentation' => 500] as $key => $max) {
                if (trim($row[$key]) === '' || strlen($row[$key]) > $max || strip_tags($row[$key]) !== $row[$key]) {
                    throw new \InvalidArgumentException('Texte invalide.');
                }
            }
            $ids[$row['id']] = true;
            $main += (int) $row['principale'];
        }
        if ($rows && $main !== 1) {
            throw new \InvalidArgumentException('Une seule principale requise.');
        }
        return $rows;
    }
}
