<?php

declare(strict_types=1);

namespace Imagine\ShippingAddresses;

/** Pure aggregate projection. Input identities are never returned. */
final class Analysis
{
    public const FIELDS = ['first_name', 'last_name', 'company', 'country', 'address_1',
        'address_2', 'city', 'state', 'postcode', 'phone'];
    public const UNKNOWN = 'inconnu après neutralisation';

    private static function metrics(array $rows, array $countries): array
    {
        $missing = array_fill_keys(array_map(static fn(string $f): string => 'shipping_' . $f, self::FIELDS), 0);
        $counts = ['subscriptions' => count($rows), 'shipping_empty' => 0, 'empty_with_billing' => 0,
            'missing_any' => 0, 'missing_required' => $missing, 'country_absent' => 0,
            'country_unknown' => 0, 'different_from_account' => 0, 'account_unavailable' => 0];
        foreach ($rows as $row) {
            $empty = true;
            $billing = false;
            $different = false;
            foreach (self::FIELDS as $field) {
                $value = (string) ($row['shipping'][$field] ?? '');
                $empty = $empty && trim($value) === '';
                $billing = $billing || trim((string) ($row['billing'][$field] ?? '')) !== '';
                if ($row['customer'] !== null) {
                    $different = $different || $value !== (string) ($row['customer'][$field] ?? '');
                }
            }
            $counts['shipping_empty'] += (int) $empty;
            $counts['empty_with_billing'] += (int) ($empty && $billing);
            $counts['different_from_account'] += (int) $different;
            $counts['account_unavailable'] += (int) ($row['customer'] === null);
            $country = (string) ($row['shipping']['country'] ?? '');
            $counts['country_absent'] += (int) (trim($country) === '');
            $counts['country_unknown'] += (int) (trim($country) !== '' && !in_array($country, $countries, true));
            $any = false;
            foreach ($row['required'] as $field) {
                if (!array_key_exists($field, $missing)) {
                    throw new \RuntimeException('A24_NATIVE_FIELDS_UNSUPPORTED');
                }
                if (trim((string) ($row['shipping'][substr($field, 9)] ?? '')) === '') {
                    $counts['missing_required'][$field]++;
                    $any = true;
                }
            }
            $counts['missing_any'] += (int) $any;
        }
        return $counts;
    }

    public static function analyse(array $rows, array $countries): array
    {
        $groups = [];
        foreach ($rows as $row) {
            $country = (string) ($row['shipping']['country'] ?? '');
            $label = trim($country) === '' ? 'country_absent'
                : (in_array($country, $countries, true) ? $country : 'country_unknown');
            $groups[$label][] = $row;
        }
        ksort($groups, SORT_STRING);
        $result = [];
        $others = [];
        foreach ($groups as $label => $members) {
            if (count($members) < 5) {
                array_push($others, ...$members);
            } else {
                $result[] = ['country' => $label, 'counts' => self::metrics($members, $countries)];
            }
        }
        if ($others !== []) {
            $result[] = ['country' => 'autres pays', 'counts' => self::metrics($others, $countries)];
        }
        return ['overall' => self::metrics($rows, $countries), 'countries' => $result];
    }
}
