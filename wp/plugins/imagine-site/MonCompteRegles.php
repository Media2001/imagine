<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;

/** Projection de lecture seulement : aucune écriture ni décision de droits. */
final class MonCompteRegles
{
    public static function date(string $value): ?DateTimeImmutable
    {
        $date = DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $value, new DateTimeZone('UTC'));
        return $date && $date->format('Y-m-d H:i:s') === $value ? $date : null;
    }

    public static function projeter(
        array $data,
        DateTimeImmutable $now,
        ?\Imagine\Pilotage\Numeros\Moteur $engine = null,
        ?int $margin = null
    ): array {
        $view = ['premier' => null, 'dernier' => null, 'echeances' => [],
            'bloc_indisponible' => 'Bloc courant indisponible — calendrier ou début non raccordé'];
        if (($data['period'] ?? '') === 'month' && (int) ($data['interval'] ?? 0) === 3) {
            for ($i = 1; $i <= 4; $i++) {
                $view['echeances'][] = ['rang' => $i, 'numero' => null, 'date' => null,
                    'etat' => 'État de paiement non raccordé', 'montant' => null, 'devise' => null];
            }
        }
        $start = self::date($data['start'] ?? '');
        if (!$start || $start > $now) {
            return $view;
        }
        $beginnings = [];
        $seen = [];
        foreach ($data['renouvellements'] ?? [] as $renewal) {
            $id = (string) $renewal['id'];
            if (isset($seen[$id])) {
                if ($seen[$id] !== $renewal) {
                    $view['bloc_indisponible'] = 'Bloc courant indisponible — renouvellement contradictoire';
                    return $view;
                }
                continue;
            }
            $seen[$id] = $renewal;
            $date = self::date($renewal['debut'] ?? '');
            if (!$date || !is_int($renewal['paiement'] ?? null) || $renewal['paiement'] > $now->getTimestamp()) {
                continue;
            }
            if ($date <= $now && $date > $start) {
                $key = $date->format('Y-m-d H:i:s');
                if (isset($beginnings[$key])) {
                    $view['bloc_indisponible'] = 'Bloc courant indisponible — plusieurs renouvellements pour le même début';
                    return $view;
                }
                $beginnings[$key] = $date;
            }
        }
        ksort($beginnings);
        $current = $beginnings ? $beginnings[array_key_last($beginnings)] : $start;
        if ($now >= $current->modify('+1 year')) {
            $view['bloc_indisponible'] = 'Bloc courant indisponible — renouvellement non raccordé';
            return $view;
        }
        $view['bloc_debut'] = $current->format('Y-m-d H:i:s');
        if (!$engine) {
            return $view;
        }
        $year = $engine->ouvrir($start);
        foreach ($beginnings as $date) {
            $year = $engine->renouveler($year, $date);
        }
        $view['premier'] = $engine->premier($year)?->id;
        $view['dernier'] = $engine->dernier($year)?->id;
        $view['bloc_indisponible'] = $view['premier'] && $view['dernier']
            ? null : 'Bloc courant indisponible — calendrier incomplet';
        $positions = $margin !== null && $margin > 0 ? $engine->echeances($year, $margin) : [];
        $numbers = $engine->numeros($year);
        foreach ($view['echeances'] as $i => &$row) {
            $row['numero'] = $numbers[$i]->id ?? null;
            $row['date'] = isset($positions[$i]) ? $positions[$i]->date->format('Y-m-d') : null;
        }
        unset($row);
        return $view;
    }

    public static function etat(array $data, DateTimeImmutable $now): string
    {
        $status = $data['status'] ?? '';
        $end = self::date($data['end'] ?? '');
        if (in_array($status, ['expired', 'cancelled'], true) || ($end && $end <= $now)) {
            return 'Expiré';
        }
        if (in_array($status, ['active', 'pending-cancel'], true)) {
            return 'Actif';
        }
        if ($status === 'pending') {
            return ($data['method'] ?? '') === 'bacs'
                ? 'Virement en attente de validation' : 'Paiement en attente de validation';
        }
        if ($status === 'on-hold') {
            if (($data['method'] ?? '') === 'bacs' && ($data['membership_pending'] ?? false)) {
                return 'Virement en attente de validation';
            }
            $from = self::date($data['grace_from'] ?? '');
            $until = self::date($data['grace_until'] ?? '');
            if ($from && $until && $from <= $now && $now < $until) {
                return 'En délai de grâce';
            }
        }
        return 'Suspendu';
    }
}
