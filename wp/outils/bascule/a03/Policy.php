<?php

declare(strict_types=1);

namespace Imagine\NonRegression;

final class Policy
{
    public static function dsn(array $config): string
    {
        if (!preg_match('/\A[A-Za-z0-9_-]+\z/D', $config['DB_NAME'])) {
            throw new \RuntimeException('A03_DB_NAME');
        }
        $host = $config['DB_HOST'];
        if (preg_match('~\Alocalhost:(/[^;\x00-\x1f]+)\z~D', $host, $match)) {
            $dsn = 'mysql:unix_socket=' . $match[1];
        } elseif (
            preg_match('/\A([A-Za-z0-9_.-]+)(?::([0-9]{1,5}))?\z/D', $host, $match)
            && (int) ($match[2] ?? 3306) <= 65535 && (int) ($match[2] ?? 3306) > 0
        ) {
            $dsn = 'mysql:host=' . $match[1] . ';port=' . ($match[2] ?? '3306');
        } else {
            throw new \RuntimeException('A03_DB_HOST');
        }
        return $dsn . ';dbname=' . $config['DB_NAME'] . ';charset=utf8mb4';
    }

    public static function verified(array $marker): bool
    {
        return ($marker['status'] ?? null) === 'verified'
            && ($marker['offline_verified'] ?? null) === true
            && ($marker['runtime_probe_passed'] ?? null) === true;
    }

    public static function renewalAllowed(bool $requested, bool $verified, bool $safeRuntime): bool
    {
        return $requested && $verified && $safeRuntime;
    }
}
