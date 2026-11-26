<?php

declare(strict_types=1);

namespace Imagine\ReaderAccounts;

final class Analysis
{
    public static function family(string $value): string
    {
        // Prefix recognition only. No validation, password trial or compatibility verdict.
        foreach (
            [
            '$wp$2y$' => 'wordpress_bcrypt', '$P$' => 'phpass', '$H$' => 'phpass_h',
            '$2a$' => 'bcrypt', '$2b$' => 'bcrypt', '$2y$' => 'bcrypt',
            '$argon2i$' => 'argon2i', '$argon2id$' => 'argon2id',
            ] as $prefix => $label
        ) {
            if (str_starts_with($value, $prefix)) {
                return $label;
            }
        }
        return $value === '' ? 'vide' : 'autre';
    }

    public static function analyse(array $rows, bool $neutralised): array
    {
        $emails = [];
        $logins = [];
        foreach ($rows as $row) {
            if ($row['email'] !== '') {
                $key = strtolower($row['email']);
                $emails[$key] = ($emails[$key] ?? 0) + 1;
            }
            $logins[strtolower($row['login'])][$row['login']] = true;
        }
        $readers = array_values(array_filter($rows, static fn(array $row): bool => !$row['admin']));
        $live = array_values(array_filter($readers, static fn(array $row): bool => $row['live']));
        $summary = static function (array $population) use ($emails, $logins, $neutralised): array {
            $families = array_fill_keys(['phpass', 'phpass_h', 'wordpress_bcrypt', 'bcrypt',
                'argon2i', 'argon2id', 'autre', 'vide'], 0);
            $mail = array_fill_keys(['email_empty', 'email_malformed', 'email_shared_case_insensitive'], 0);
            $login = array_fill_keys(['login_equals_email', 'login_case_collision'], 0);
            foreach ($population as $row) {
                $families[self::family($row['hash'])]++;
                $mail['email_empty'] += (int) ($row['email'] === '');
                $mail['email_malformed'] += (int) ($row['email'] !== '' && !$row['email_valid']);
                $mail['email_shared_case_insensitive'] += (int) ($row['email'] !== ''
                    && ($emails[strtolower($row['email'])] ?? 0) > 1);
                $login['login_equals_email'] += (int) ($row['email'] !== '' && $row['login'] === $row['email']);
                $login['login_case_collision'] += (int) (count($logins[strtolower($row['login'])]) > 1);
            }
            return ['accounts' => count($population),
                'families' => $neutralised ? 'inconnu après neutralisation' : self::pool($families),
                'emails' => $neutralised ? 'inconnu après neutralisation' : self::pool($mail),
                'logins' => $neutralised ? 'inconnu après neutralisation' : self::pool($login)];
        };
        return ['readers' => $summary($readers), 'live_readers' => $summary($live),
            'without_commerce' => self::pool(['without_order_or_subscription' => count(array_filter(
                $readers,
                static fn(array $row): bool => !$row['commerce']
            ))])];
    }

    public static function pool(array $counts): array
    {
        $result = ['groups' => [], 'autres' => 0];
        foreach ($counts as $label => $count) {
            if ($count >= 5) {
                $result['groups'][] = ['label' => $label, 'accounts' => $count];
            } else {
                $result['autres'] += $count;
            }
        }
        return $result;
    }
}
