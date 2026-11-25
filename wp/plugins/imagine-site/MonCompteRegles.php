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
        $view = self::reglements($data, $view, $now);
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

    /** Ordre initial puis relations natives triées ; jamais la date de paiement comme date C05. */
    private static function reglements(array $data, array $view, DateTimeImmutable $now): array
    {
        $view['avertissements'] = [];
        if (!$view['echeances']) {
            return $view;
        }
        $orders = [];
        $unplaced = false;
        foreach ($data['orders'] ?? [] as $order) {
            if (($data['owner'] ?? 0) <= 0 || (int) $order['owner'] !== (int) $data['owner']) {
                $view['avertissements'][] = 'Commande liée hors propriétaire ignorée';
                continue;
            }
            $created = self::date($order['created'] ?? '');
            $explicit = $order['bloc_debut'] ?? '';
            if ($order['initial'] && $view['bloc_debut'] !== $data['start']) {
                continue;
            }
            if ($explicit !== '' && $explicit !== $view['bloc_debut']) {
                continue;
            }
            if (!$order['initial'] && $explicit === '' && $created && $order['created'] < $view['bloc_debut']) {
                continue;
            }
            if (!$created && !$order['initial']) {
                $view['avertissements'][] = 'Rattachement ambigu — commande #' . $order['id'] . ' sans date native exploitable';
                $unplaced = true;
                continue;
            }
            $id = (int) $order['id'];
            if (isset($orders[$id])) {
                $previous = $orders[$id];
                unset($previous['ambigu']);
                if ($previous !== $order) {
                    $view['avertissements'][] = 'Rattachement contradictoire — commande #' . $id;
                    $orders[$id]['ambigu'] = true;
                }
                continue;
            }
            $orders[$id] = $order;
        }
        $groups = [];
        foreach ($orders as $order) {
            $key = $order['initial'] ? '0' : '1' . $order['created'];
            $groups[$key][] = $order;
        }
        // La commande mère manquante ne transforme pas le premier renouvellement en initial.
        if ($view['bloc_debut'] === $data['start'] && !isset($groups['0'])) {
            $groups['0'] = [null];
        }
        ksort($groups);
        $slots = [];
        foreach ($groups as $group) {
            $ambiguous = count($group) > 1 || !empty($group[0]['ambigu']) || $group[0] === null;
            foreach ($group as $order) {
                $slots[] = ['order' => $order, 'ambigu' => $ambiguous];
                if ($ambiguous && $order) {
                    $view['avertissements'][] = 'Rattachement ambigu — commande #' . $order['id']
                        . ' (' . $order['status'] . ', ' . $order['total'] . ' ' . $order['currency'] . ')';
                }
            }
        }
        if (count($slots) > 4) {
            $view['avertissements'][] = 'Rattachement ambigu — plus de quatre commandes dans le bloc';
        }
        foreach ($view['echeances'] as $i => &$row) {
            $slot = $slots[$i] ?? null;
            $order = $slot['order'] ?? null;
            $ambiguous = ($slot['ambigu'] ?? false) || (!$slot && $unplaced);
            $row['commande'] = !$ambiguous ? ($order['id'] ?? null) : null;
            $row['montant'] = $ambiguous ? null : ($order['total'] ?? ($data['total'] ?? null));
            $row['devise'] = $ambiguous ? null : ($order['currency'] ?? ($data['currency'] ?? null));
            $paid = $order ? self::date($order['paid_at'] ?? '') : null;
            $row['etat'] = $ambiguous ? 'Rattachement ambigu — voir détail' : (!$order ? 'À venir'
                : ($order['status'] === 'failed' ? 'Échouée'
                    : ($order['paid'] && $paid && $paid <= $now ? 'Payée' : 'Non réglée — commande native en attente')));
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
