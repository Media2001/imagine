<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;

/** Stockage du parcours ; la décision métier reste exclusivement dans C06. */
final class Decouverte
{
    public const OPTION = 'imagine_decouverte_reglages';

    public static function defauts(): array
    {
        return ['ouverture' => 'fermee', 'forme' => 'articles', 'jours' => 7, 'nombre' => 2, 'numeros' => []];
    }

    public static function key(int $userId): string
    {
        if ($userId <= 0) {
            throw new \InvalidArgumentException('Compte requis.');
        }
        return 'imagine_decouverte_compte_' . $userId;
    }

    public static function verifie(int $userId): bool
    {
        $user = get_userdata($userId);
        return $user && trim((string) $user->first_name) !== '' && trim((string) $user->last_name) !== ''
            && is_email($user->user_email) && get_user_meta($userId, 'imagine_email_confirme', true) === '1';
    }

    public static function reglages(): array
    {
        $value = get_option(self::OPTION, self::defauts());
        return self::valide($value) ? $value : self::defauts();
    }

    public static function valide(mixed $value): bool
    {
        if (!is_array($value) || count($value) !== 5 || array_diff(array_keys(self::defauts()), array_keys($value))
            || !in_array($value['ouverture'], ['fermee', 'premiere_lecture'], true)
            || !in_array($value['forme'], ['articles', 'duree'], true)
            || !is_int($value['jours']) || $value['jours'] < 1 || $value['jours'] > 365
            || !is_int($value['nombre']) || $value['nombre'] < 1 || $value['nombre'] > 100
            || !is_array($value['numeros']) || !array_is_list($value['numeros'])
            || count($value['numeros']) !== count(array_unique($value['numeros'], SORT_REGULAR))) {
            return false;
        }
        foreach ($value['numeros'] as $id) {
            if (!is_string($id) || !preg_match('/^[1-9][0-9]*$/D', $id)) {
                return false;
            }
        }
        return true;
    }

    /** INSERT IGNORE : index unique natif, jamais d'UPSERT susceptible de recréditer. */
    public static function ouvrir(int $userId, DateTimeImmutable $now): ?array
    {
        $settings = self::reglages();
        if ($settings['ouverture'] !== 'premiere_lecture' || !$settings['numeros'] || !self::verifie($userId)) {
            return null;
        }
        $key = self::key($userId);
        $state = get_option($key, null);
        if ($state === null) {
            $initial = ['debut' => $now->setTimezone(new DateTimeZone('UTC'))->format('Y-m-d H:i:s'),
                'reglages' => $settings, 'articles' => []];
            global $wpdb;
            $written = $wpdb->query($wpdb->prepare(
                "INSERT IGNORE INTO {$wpdb->options} (option_name, option_value, autoload) VALUES (%s, %s, 'off')",
                $key,
                maybe_serialize($initial)
            ));
            if ($written === false) {
                return null;
            }
            wp_cache_delete('notoptions', 'options');
            wp_cache_delete($key, 'options');
            $state = get_option($key, null); // Relit même en cas de course d'ouverture.
        }
        return self::etatValide($state) ? $state : null;
    }

    private static function etatValide(mixed $state): bool
    {
        if (!is_array($state) || count($state) !== 3 || !isset($state['debut'], $state['reglages'], $state['articles'])
            || !is_string($state['debut']) || !self::valide($state['reglages'])
            || !is_array($state['articles']) || !array_is_list($state['articles'])
            || count($state['articles']) !== count(array_unique($state['articles'], SORT_REGULAR))) {
            return false;
        }
        $date = DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $state['debut'], new DateTimeZone('UTC'));
        if (!$date || $date->format('Y-m-d H:i:s') !== $state['debut']) {
            return false;
        }
        foreach ($state['articles'] as $id) {
            if (!is_int($id) || $id <= 0) {
                return false;
            }
        }
        return true;
    }
}
