<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Projections pures : aucun statut ni droit d'accès n'est écrit ici. */
final class EcheancesRegles
{
    public static function mandats(array $rows, int $now, int $days): array
    {
        if (!in_array($days, [30, 90, 180], true)) {
            throw new \InvalidArgumentException('Période invalide.');
        }
        $out = [];
        $seen = [];
        foreach ($rows as $row) {
            if ($row['methode'] !== 'imagine_papier' || !in_array($row['etat'], ['active', 'on-hold'], true)) {
                continue;
            }
            $row['reference'] = trim($row['reference']) === '' ? 'Référence manquante' : $row['reference'];
            $due = array_filter($row['renouvellements'] ?? [], static fn ($order) =>
                !$order['paye'] && $order['date_payee'] === 0
                && in_array($order['etat'], ['pending', 'on-hold', 'failed'], true)
                && $order['creation'] > 0 && $order['creation'] <= $now);
            if ($due !== []) {
                foreach ($due as $order) {
                    if (!isset($seen[$order['id']])) {
                        $out[] = array_replace($row, ['id' => $order['id'], 'souscription' => $row['id'],
                            'etat' => $order['etat'], 'montant' => $order['montant'], 'devise' => $order['devise'],
                            'echeance' => $order['creation'], 'type' => 'commande']);
                        $seen[$order['id']] = true;
                    }
                }
                // Une dette native remplace la projection future, elle ne s'y ajoute pas.
                continue;
            }
            if ($row['etat'] === 'active' && $row['prochaine'] > 0 && $row['prochaine'] <= $now + $days * 86400
                && ($row['fin'] === 0 || ($row['fin'] > $now && $row['prochaine'] < $row['fin']))) {
                $out[] = $row + ['echeance' => $row['prochaine']];
            }
        }
        usort($out, static fn ($a, $b) => [$a['echeance'], $a['id']] <=> [$b['echeance'], $b['id']]);
        return $out;
    }

    /** Flux fourni par l'appelant : aucune écriture de fichier ni colonne libre. */
    public static function csv($stream, array $rows): void
    {
        fputcsv($stream, ['Abonné', 'Montant', 'Devise', 'Référence du mandat', 'Échéance (UTC)'], ';', '"', '');
        foreach ($rows as $row) {
            $cells = [$row['abonne'], $row['montant'], $row['devise'], $row['reference'], gmdate('Y-m-d H:i:s', $row['echeance'])];
            $cells = array_map(static function ($value): string {
                $value = (string) $value;
                return preg_match('/^[\\x00-\\x20\\x7f\\p{Z}]*[=+@-]/u', $value) ? "'" . $value : $value;
            }, $cells);
            if (fputcsv($stream, $cells, ';', '"', '') === false) {
                throw new \RuntimeException('Flux CSV indisponible.');
            }
        }
    }

    public static function paiements(array $rows, string $view): array
    {
        if (!in_array($view, ['attente', 'virements', 'echecs'], true)) {
            throw new \InvalidArgumentException('Vue invalide.');
        }
        $out = array_filter($rows, static function ($row) use ($view): bool {
            if ($row['paye'] || $row['date_payee'] > 0) {
                return false;
            }
            if ($view === 'echecs') {
                return $row['etat'] === 'failed';
            }
            return in_array($row['etat'], ['pending', 'on-hold'], true)
                && ($view !== 'virements' || $row['methode'] === 'bacs');
        });
        usort($out, static fn ($a, $b) => [$a['creation'], $a['id']] <=> [$b['creation'], $b['id']]);
        return $out;
    }

    public static function echeances(array $rows, int $now, int $days): array
    {
        if (!in_array($days, [30, 90, 180], true)) {
            throw new \InvalidArgumentException('Période invalide.');
        }
        $out = [];
        foreach ($rows as $row) {
            if (!in_array($row['etat'], ['active', 'pending-cancel', 'on-hold', 'pending'], true)) {
                continue;
            }
            $dates = array_filter([$row['prochaine'], $row['fin']], static fn ($date) => $date >= $now && $date > 0);
            if ($dates !== [] && min($dates) <= $now + $days * 86400) {
                $out[] = $row + ['echeance' => min($dates)];
            }
        }
        usort($out, static fn ($a, $b) => [$a['echeance'], $a['id']] <=> [$b['echeance'], $b['id']]);
        return $out;
    }
}
