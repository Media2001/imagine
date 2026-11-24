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
        $state = self::etat($userId);
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
            $state = self::etat($userId); // Relit même en cas de course d'ouverture.
        }
        return self::etatValide($state) ? $state : null;
    }

    /** Lecture fraîche : le cache d'options ne peut masquer une consommation concurrente. */
    public static function etat(int $userId): ?array
    {
        global $wpdb;
        $raw = $wpdb->get_var($wpdb->prepare("SELECT option_value FROM {$wpdb->options} WHERE option_name = %s", self::key($userId)));
        if ($wpdb->last_error !== '') {
            throw new \RuntimeException('État découverte indisponible.');
        }
        if ($raw === null) {
            return null;
        }
        $state = maybe_unserialize($raw);
        if (!self::etatValide($state)) {
            throw new \RuntimeException('État découverte invalide, jamais réinitialisé.');
        }
        return $state;
    }

    /** Le moteur C06 arbitre aussi les droits prioritaires : ils ne consomment jamais. */
    public static function decider(array $content, array $visitor, \Imagine\Pilotage\Robots\Decision $robot,
        DateTimeImmutable $now, int $articleId): \Imagine\Pilotage\Acces\Decision
    {
        $base = Paywall::deciderContenu($content, $visitor, $robot, $now);
        if ($base->complet || !$visitor['identifie'] || $content['type'] !== 'article'
            || !$content['reserve'] || $content['sortie'] > $now) {
            return $base;
        }
        $id = get_current_user_id();
        $settings = self::reglages();
        if ($id <= 0 || $settings['ouverture'] !== 'premiere_lecture'
            || !in_array($content['numero'], $settings['numeros'], true)) {
            return $base;
        }
        try {
            for ($attempt = 0; $attempt < 5; ++$attempt) {
                $state = self::ouvrir($id, $now);
                if (!$state) {
                    return $base;
                }
                $policy = $state['reglages'];
                $seen = in_array($articleId, $state['articles'], true);
                $rights = $visitor;
                $rights['droits'][] = ['type' => 'decouverte',
                    'debut' => new DateTimeImmutable($state['debut'], new DateTimeZone('UTC')),
                    'compte_verifie' => self::verifie($id),
                    'consommes' => count($state['articles']) - ($seen ? 1 : 0)];
                $content['decouverte'] = true;
                $rule = $policy['forme'] === 'articles'
                    ? new \Imagine\Pilotage\Acces\NombreArticlesDecouverte($policy['nombre'], $policy['numeros'], false)
                    : new \Imagine\Pilotage\Acces\DureeDecouverte($policy['jours'] * DAY_IN_SECONDS, $policy['numeros'], false);
                $decision = (new \Imagine\Pilotage\Acces\Moteur())->decider($content, $rights, $robot, $now,
                    $rule, (new \Imagine\Pilotage\Acces\AdministrationReglages())->lire());
                if (!$decision->complet || $seen) {
                    return $decision;
                }
                $next = $state;
                $next['articles'][] = $articleId;
                global $wpdb;
                // Compare-and-swap binaire : une lecture concurrente doit revalider le quota.
                $updated = $wpdb->query($wpdb->prepare(
                    "UPDATE {$wpdb->options} SET option_value = %s WHERE option_name = %s AND BINARY option_value = BINARY %s",
                    maybe_serialize($next), self::key($id), maybe_serialize($state)
                ));
                wp_cache_delete(self::key($id), 'options');
                if ($updated === 1) {
                    if (self::etat($id) === null) {
                        return $base;
                    }
                    return $decision;
                }
                if ($updated === false) {
                    return $base;
                }
            }
        } catch (\Throwable) {
            return $base;
        }
        return $base; // Contention persistante : fermé, pas de droit présumé.
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
