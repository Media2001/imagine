<?php

declare(strict_types=1);

namespace Imagine\SavedPayments;

final class Analysis
{
    public const UNKNOWN = 'inconnu après neutralisation';
    public const LIVE = ['active', 'pending', 'on-hold', 'pending-cancel'];
    public const GATEWAYS = ['stripe', 'stripe_sepa', 'paypal', 'ppec_paypal', 'ppcp-gateway',
        'ppcp-credit-card-gateway', 'woocommerce_payments', 'bacs', 'cheque', 'cod'];

    public static function gateway(string $gateway): string
    {
        return $gateway === '' ? 'aucune' : (in_array($gateway, self::GATEWAYS, true) ? $gateway : 'autre');
    }

    public static function tokenType(string $type, string $gateway): string
    {
        return match ($type) {
            'CC' => 'carte',
            'SEPA' => 'mandat_sepa',
            'eCheck' => $gateway === 'stripe_sepa' ? 'mandat_sepa' : 'autre',
            '' => 'illisible',
            default => 'autre',
        };
    }

    public static function clock(string $date): \DateTimeImmutable
    {
        $clock = \DateTimeImmutable::createFromFormat('!Y-m-d\TH:i:sP', $date, new \DateTimeZone('UTC'));
        if (!$clock || $clock->format('Y-m-d\TH:i:sP') !== $date || !str_ends_with($date, '+00:00')) {
            throw new \RuntimeException('A27_CLOCK_INVALID');
        }
        return $clock;
    }

    public static function expiry(string $year, string $month, string $audit): string
    {
        $now = self::clock($audit);
        if (!preg_match('/\A[1-9][0-9]{3}\z/D', $year) || !preg_match('/\A(?:0[1-9]|1[0-2])\z/D', $month)) {
            return 'illisible';
        }
        $last = new \DateTimeImmutable($year . '-' . $month . '-01T00:00:00+00:00');
        $end = $last->modify('first day of next month')->modify('-1 second');
        if ($end < $now) {
            return 'expired';
        }
        // Six calendar months, clamped day, same UTC time; not 180 days.
        $target = $now->modify('first day of this month')->modify('+6 months');
        $target = $target->setDate(
            (int) $target->format('Y'),
            (int) $target->format('m'),
            min((int) $now->format('d'), (int) $target->format('t'))
        );
        return $end <= $target ? 'within_six_months' : 'later';
    }

    public static function pool(array $rows, string $field): array
    {
        $buckets = [];
        foreach ($rows as $row) {
            $gateway = self::gateway($row['gateway']);
            $key = $gateway . ':' . $row[$field];
            $buckets[$key] ??= ['gateway' => $gateway, $field => $row[$field], 'count' => 0];
            $buckets[$key]['count']++;
        }
        ksort($buckets, SORT_STRING);
        $result = ['groups' => [], 'autres' => 0];
        foreach ($buckets as $bucket) {
            if ($bucket['count'] < 5) {
                $result['autres'] += $bucket['count'];
            } else {
                $result['groups'][] = $bucket;
            }
        }
        return $result;
    }

    /** Values and IDs remain private in memory. No identity/prefix heuristics. */
    public static function reference(array $subscription, array $tokens): array
    {
        $gateway = $subscription['gateway'];
        $user = $subscription['user'];
        $owned = array_filter($tokens, static fn(array $t): bool => $user > 0 && $t['account']
            && $t['user'] === $user && $t['gateway'] === $gateway && $t['value'] !== '');
        $ids = array_values(array_unique($subscription['tokens']));
        $linked = array_values(array_filter($owned, static fn(array $t): bool => in_array($t['id'], $ids, true)));
        $metadata = $subscription['metadata'];
        $invalid = false;
        $refs = [];
        foreach ($metadata as $key => $value) {
            if (!is_string($value)) {
                $invalid = true;
            } elseif ($value !== '') {
                $refs[$value] = true;
            }
        }
        if ($invalid) {
            return ['type' => 'illisible', 'link' => 'unknown', 'expiry' => null, 'present' => true];
        }
        if ($refs) {
            $matches = array_values(array_filter($owned, static fn(array $t): bool => isset($refs[$t['value']])));
            // Distinct nonempty reference fields can represent different instruments.
            if (count($refs) !== 1 || count($matches) > 1) {
                return ['type' => 'illisible', 'link' => 'unknown', 'expiry' => null, 'present' => true];
            }
            if ($ids && (count($matches) !== 1 || !in_array($matches[0]['id'], $ids, true))) {
                return ['type' => 'illisible', 'link' => 'unknown', 'expiry' => null, 'present' => true];
            }
            if (count($matches) === 1 && (!$ids || in_array($matches[0]['id'], $ids, true))) {
                $t = $matches[0];
                return ['type' => $t['readable'] ? self::tokenType($t['type'], $gateway) : 'illisible',
                    'link' => 'linked', 'expiry' => [$t['year'], $t['month']], 'present' => true];
            }
            $type = in_array($gateway, ['paypal', 'ppec_paypal', 'ppcp-gateway'], true) ? 'accord_paypal'
                : ($gateway === 'stripe_sepa' ? 'mandat_sepa' : 'illisible');
            return ['type' => $type, 'link' => $ids ? 'unknown' : 'unlinked', 'expiry' => null, 'present' => true];
        }
        if (count($linked) === 1 && count($ids) === 1) {
            $t = $linked[0];
            return ['type' => $t['readable'] ? self::tokenType($t['type'], $gateway) : 'illisible',
                'link' => 'linked', 'expiry' => [$t['year'], $t['month']], 'present' => true];
        }
        $present = (bool) $ids || $subscription['reference'] !== 'absent';
        return ['type' => 'illisible', 'link' => $ids && !$linked ? 'unlinked' : 'unknown',
            'expiry' => null, 'present' => $present];
    }

    public static function analyse(array $subscriptions, array $tokens, string $audit, bool $neutralised): array
    {
        self::clock($audit);
        if ($neutralised) {
            return array_fill_keys(['automatic', 'cards', 'relations'], self::UNKNOWN);
        }
        $automatic = [];
        $cards = [];
        $relations = [];
        $live = [];
        foreach ($subscriptions as $s) {
            if (!in_array($s['status'], self::LIVE, true)) {
                continue;
            }
            if ($s['user'] > 0) {
                $live[$s['user']] = true;
            }
            $ref = self::reference($s, $tokens);
            if ($ref['present'] && $ref['link'] !== 'linked') {
                $relations[] = ['gateway' => $s['gateway'], 'metric' => $ref['link'] === 'unlinked'
                    ? 'subscriptions_unlinked' : 'subscriptions_link_unknown'];
            }
            if ($s['manual'] || !$ref['present']) {
                continue;
            }
            $automatic[] = ['gateway' => $s['gateway'], 'type' => $ref['type']];
            if ($ref['type'] === 'carte') {
                $date = $ref['expiry'] ?? ['', ''];
                $cards[] = ['gateway' => $s['gateway'], 'expiry' => self::expiry($date[0], $date[1], $audit)];
            }
        }
        $accounts = [];
        foreach ($tokens as $t) {
            if ($t['user'] <= 0 || !$t['account']) {
                $relations[] = ['gateway' => $t['gateway'], 'metric' => 'tokens_account_unknown'];
                continue;
            }
            $accounts[$t['user']] = ($accounts[$t['user']] ?? 0) + 1;
            if (!isset($live[$t['user']])) {
                $relations[] = ['gateway' => $t['gateway'], 'metric' => 'tokens_without_living_subscription'];
            }
        }
        foreach ($accounts as $count) {
            if ($count > 1) {
                $relations[] = ['gateway' => 'autre', 'metric' => 'accounts_multiple_tokens'];
            }
        }
        return ['automatic' => self::pool($automatic, 'type'), 'cards' => self::pool($cards, 'expiry'),
            'relations' => self::pool($relations, 'metric')];
    }
}
