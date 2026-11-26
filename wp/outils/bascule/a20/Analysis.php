<?php

declare(strict_types=1);

namespace Imagine\SubscriptionPrices;

final class Analysis
{
    private const COUNTRIES = 'AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW';

    public static function analyse(array $subscriptions, string $siteCurrency): array
    {
        $states = ['active', 'pending', 'on-hold', 'pending-cancel'];
        $result = ['live_subscriptions' => 0, 'products' => [], 'countries' => [],
            'other_countries' => ['count' => 0, 'with_shipping' => 0],
            'unknown_country' => ['count' => 0, 'with_shipping' => 0],
            'multiple_product_lines' => 0, 'without_product_line' => 0,
            'with_fee_line' => 0, 'with_shipping_line' => 0,
            'foreign_currency' => 0, 'zero_recurring_total' => 0];
        $products = [];
        $countries = [];
        foreach ($subscriptions as $row) {
            if (!in_array($row['status'], $states, true)) {
                continue;
            }
            $result['live_subscriptions']++;
            $result['multiple_product_lines'] += (int) ($row['line_count'] > 1);
            $result['without_product_line'] += (int) ($row['line_count'] === 0);
            $result['with_fee_line'] += (int) $row['fees'];
            $result['with_shipping_line'] += (int) $row['shipping'];
            $result['foreign_currency'] += (int) ($row['currency'] !== $siteCurrency);
            $amount = self::decimal($row['total']);
            $result['zero_recurring_total'] += (int) ($amount === '0.00');
            $country = $row['country'];
            $countries[$country] ??= ['country' => $country, 'count' => 0, 'with_shipping' => 0];
            $countries[$country]['count']++;
            $countries[$country]['with_shipping'] += (int) $row['shipping'];
            $seen = [];
            foreach ($row['products'] as $item) {
                $key = $item['product'] . ':' . $item['variation'];
                if (isset($seen[$key])) {
                    continue;
                }
                $seen[$key] = true;
                $products[$key] ??= ['product' => $item['product'], 'variation' => $item['variation'],
                    'count' => 0, 'states' => array_fill_keys($states, 0), 'schedules' => [],
                    'non_annual' => 0, 'amounts' => [], 'other_amounts' => 0];
                $p = &$products[$key];
                $p['count']++;
                $p['states'][$row['status']]++;
                $scheduleKey = $row['period'] . ':' . $row['interval'];
                $p['schedules'][$scheduleKey] ??= ['interval' => $row['interval'],
                    'period' => $row['period'], 'count' => 0];
                $p['schedules'][$scheduleKey]['count']++;
                $p['non_annual'] += (int) !(($row['period'] === 'year' && $row['interval'] === 1)
                    || ($row['period'] === 'month' && $row['interval'] === 12));
                $amountKey = $row['currency'] . ':' . $amount;
                $p['amounts'][$amountKey] ??= ['currency' => $row['currency'], 'amount' => $amount, 'count' => 0];
                $p['amounts'][$amountKey]['count']++;
                unset($p);
            }
        }
        foreach ($products as $p) {
            $p['schedules'] = array_values($p['schedules']);
            usort($p['schedules'], static fn(array $a, array $b): int =>
                [$a['period'], $a['interval']] <=> [$b['period'], $b['interval']]);
            $visible = [];
            ksort($p['amounts'], SORT_STRING);
            foreach ($p['amounts'] as $amount) {
                if ($amount['count'] < 5) {
                    $p['other_amounts'] += $amount['count'];
                } else {
                    $visible[] = $amount;
                }
            }
            $p['amounts'] = $visible;
            $result['products'][] = $p;
        }
        usort($result['products'], static fn(array $a, array $b): int =>
            [$a['product'], $a['variation']] <=> [$b['product'], $b['variation']]);
        ksort($countries, SORT_STRING);
        foreach ($countries as $country) {
            if ($country['count'] < 5) {
                $result['other_countries']['count'] += $country['count'];
                $result['other_countries']['with_shipping'] += $country['with_shipping'];
            } else {
                $result['countries'][] = $country;
            }
        }
        return $result;
    }

    private static function decimal(string $value): string
    {
        if (!preg_match('/\A(-?)([0-9]{1,18})(?:\.([0-9]{1,12}))?\z/D', $value, $m)) {
            throw new \RuntimeException('A20_DATA_UNSUPPORTED');
        }
        $whole = ltrim($m[2], '0');
        $whole = $whole === '' ? '0' : $whole;
        $fraction = rtrim($m[3] ?? '', '0');
        $sign = ($whole !== '0' || $fraction !== '') ? $m[1] : '';
        return $sign . $whole . '.' . str_pad($fraction, 2, '0');
    }
}
