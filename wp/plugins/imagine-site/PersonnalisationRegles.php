<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Questions et étiquettes fermées ; aucune dépendance à WordPress. */
final class PersonnalisationRegles
{
    public static function catalogue(mixed $rows): array
    {
        if (!is_array($rows) || !array_is_list($rows) || count($rows) > 20) {
            throw new \InvalidArgumentException('Questions invalides.');
        }
        $ids = $choices = [];
        foreach ($rows as $row) {
            if (!is_array($row) || count($row) !== 4 || !self::id($row['id'] ?? null)
                || isset($ids[$row['id']]) || !self::texte($row['titre'] ?? null)
                || !is_bool($row['multiple'] ?? null) || !is_array($row['choix'] ?? null)
                || !array_is_list($row['choix']) || !$row['choix'] || count($row['choix']) > 30) {
                throw new \InvalidArgumentException('Question invalide.');
            }
            $ids[$row['id']] = true;
            foreach ($row['choix'] as $choice) {
                if (!is_array($choice) || count($choice) !== 2 || !self::id($choice['id'] ?? null)
                    || isset($choices[$choice['id']]) || !self::texte($choice['titre'] ?? null)) {
                    throw new \InvalidArgumentException('Choix invalide.');
                }
                $choices[$choice['id']] = true;
            }
        }
        return $rows;
    }

    public static function repondre(array $rows, array $old, array $answers, string $now, bool $erase = false): array
    {
        self::catalogue($rows);
        if (!self::date($now) || array_diff(array_keys($answers), array_column($rows, 'id'))) {
            throw new \InvalidArgumentException('Réponse invalide.');
        }
        foreach ($rows as $row) {
            $selected = $answers[$row['id']] ?? [];
            if (!is_array($selected) || !array_is_list($selected)
                || (!$row['multiple'] && count($selected) > 1)) {
                throw new \InvalidArgumentException('Réponse invalide.');
            }
            foreach ($selected as $value) {
                if (!is_string($value) || !in_array($value, array_column($row['choix'], 'id'), true)) {
                    throw new \InvalidArgumentException('Réponse inconnue.');
                }
            }
            $selected = array_values(array_unique($selected));
            sort($selected, SORT_STRING);
            if (!$selected) {
                unset($old[$row['id']]);
            } elseif (($old[$row['id']]['choix'] ?? null) !== $selected) {
                $old[$row['id']] = ['choix' => $selected, 'date_utc' => $now];
            }
        }
        return $erase ? [] : $old;
    }

    public static function transmissible(array $consent, bool $newsletter, bool $email): bool
    {
        return ($consent['accord'] ?? null) === true && self::date($consent['date_utc'] ?? null)
            && $newsletter && $email;
    }

    private static function date(mixed $date): bool
    {
        return is_string($date) && preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/D', $date) === 1;
    }

    public static function id(mixed $id): bool
    {
        return is_string($id) && preg_match('/^[a-z][a-z0-9_-]{0,49}$/D', $id) === 1;
    }

    private static function texte(mixed $text): bool
    {
        return is_string($text) && mb_check_encoding($text, 'UTF-8') && trim($text) !== ''
            && mb_strlen($text, 'UTF-8') <= 150 && strip_tags($text) === $text;
    }
}
