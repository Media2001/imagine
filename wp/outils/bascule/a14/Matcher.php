<?php

declare(strict_types=1);

namespace Imagine\Contacts;

final class Matcher
{
    public static function normalise(string $email): string
    {
        return strtolower(preg_replace('/\s+/u', '', $email));
    }

    public static function build(array $contacts, array $accounts): array
    {
        $index = [];
        $unmatchable = 0;
        foreach ($accounts as $account) {
            if ($account['technical']) {
                continue;
            }
            $email = self::normalise($account['email']);
            if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
                $unmatchable++;
                continue;
            }
            $index[$email][] = $account;
        }
        $matched = [];
        $seen = [];
        $groups = [];
        $anomalies = [];
        $invalid = 0;
        $statuses = ['inscrit' => 0, 'desinscrit' => 0, 'bloque' => 0, 'inconnu' => 0];
        foreach ($contacts as $contact) {
            if (!isset($statuses[$contact['status']]) || !is_int($contact['line']) || $contact['line'] < 2) {
                throw new \RuntimeException('A14_CONTACT_FORMAT');
            }
            $statuses[$contact['status']]++;
            $email = self::normalise($contact['email']);
            if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
                $invalid++;
                $anomalies[] = ['line' => $contact['line'], 'reason' => 'Adresse électronique invalide'];
                continue;
            }
            $groups[$email][] = $contact['line'];
            if (isset($index[$email])) {
                $seen[$email] = true;
                $matched[] = [
                    'line' => $contact['line'], 'active_subscription' => $index[$email][0]['active'],
                    'status' => $contact['status'], 'cooperateur' => '', 'tarif' => '',
                ];
            }
        }
        $without = 0;
        foreach ($index as $email => $group) {
            if (!isset($seen[$email])) {
                $without += count($group);
            }
        }
        $duplicateLines = 0;
        foreach ($groups as $lines) {
            if (count($lines) > 1) {
                $duplicateLines += count($lines);
                foreach ($lines as $line) {
                    $anomalies[] = ['line' => $line, 'reason' => 'Doublon dans le fichier'];
                }
            }
        }
        usort($anomalies, static fn(array $a, array $b): int => $a['line'] <=> $b['line']);
        return [
            'counts' => [
                'contacts_total' => count($contacts), 'contacts_with_account' => count($matched),
                'contacts_without_account' => count($contacts) - $invalid - count($matched),
                'accounts_without_contact' => $without, 'accounts_unmatchable' => $unmatchable,
                'invalid_contact_lines' => $invalid, 'duplicate_contact_lines' => $duplicateLines,
                'unsubscribed_contacts' => $statuses['desinscrit'], 'blocked_contacts' => $statuses['bloque'],
            ],
            'matched' => $matched, 'anomalies' => $anomalies,
        ];
    }
}
