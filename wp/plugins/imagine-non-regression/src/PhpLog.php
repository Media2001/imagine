<?php

declare(strict_types=1);

namespace Imagine\NonRegression;

/** Read native PHP UTC file logs only; never export messages, filenames or traces. */
final class PhpLog
{
    public static function timestamp(string $value): int
    {
        $date = \DateTimeImmutable::createFromFormat('!Y-m-d\TH:i:s\Z', $value, new \DateTimeZone('UTC'));
        if (!$date || $date->format('Y-m-d\TH:i:s\Z') !== $value) {
            throw new \RuntimeException('A03_PHP_LOG_WINDOW');
        }
        return $date->getTimestamp();
    }

    public static function read(string $path, string $from, string $until): array
    {
        $start = self::timestamp($from);
        $end = self::timestamp($until);
        if ($end < $start || $end - $start > 86400) {
            throw new \RuntimeException('A03_PHP_LOG_WINDOW');
        }
        clearstatcache(true, $path);
        $stat = @lstat($path);
        if (
            $stat === false || ($stat['mode'] & 0170000) !== 0100000 || ($stat['mode'] & 0444) === 0
            || $stat['size'] > 16777216 || realpath($path) !== $path || !is_readable($path)
        ) {
            throw new \RuntimeException('A03_PHP_LOG_READ');
        }
        $stream = @fopen($path, 'rb');
        if ($stream === false) {
            throw new \RuntimeException('A03_PHP_LOG_READ');
        }
        try {
            $opened = fstat($stream);
            if (!$opened || $opened['ino'] !== $stat['ino'] || $opened['dev'] !== $stat['dev']) {
                throw new \RuntimeException('A03_PHP_LOG_READ');
            }
            $text = stream_get_contents($stream, 16777217);
            clearstatcache(true, $path);
            $after = @lstat($path);
            $finished = fstat($stream);
            foreach (['ino', 'dev', 'size', 'mtime', 'ctime'] as $key) {
                if (!$after || !$finished || $after[$key] !== $stat[$key] || $finished[$key] !== $stat[$key]) {
                    throw new \RuntimeException('A03_PHP_LOG_READ');
                }
            }
            if ($text === false || strlen($text) !== $stat['size'] || !feof($stream)) {
                throw new \RuntimeException('A03_PHP_LOG_READ');
            }
        } finally {
            fclose($stream);
        }
        $errors = 0;
        $hasRecord = false;
        if ($text !== '' && !str_ends_with($text, "\n")) {
            throw new \RuntimeException('A03_PHP_LOG_FORMAT');
        }
        foreach (explode("\n", rtrim($text, "\n")) as $line) {
            if (strlen($line) > 65536) {
                throw new \RuntimeException('A03_PHP_LOG_FORMAT');
            }
            if ($line === '') {
                continue;
            }
            if (preg_match('/\A\[([0-9]{2}-[A-Za-z]{3}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}) UTC\] /', $line, $m)) {
                $date = \DateTimeImmutable::createFromFormat('!d-M-Y H:i:s', $m[1], new \DateTimeZone('UTC'));
                if (!$date || $date->format('d-M-Y H:i:s') !== $m[1]) {
                    throw new \RuntimeException('A03_PHP_LOG_FORMAT');
                }
                $timestamp = $date->getTimestamp();
                // A custom error_log record is also a diagnostic; do not silently whitelist it.
                $errors += (int) ($timestamp >= $start && $timestamp <= $end);
                $hasRecord = true;
            } elseif (!$hasRecord || !preg_match('/\A(?:Stack trace:|#[0-9]+ |\s+thrown in )/', $line)) {
                throw new \RuntimeException('A03_PHP_LOG_FORMAT');
            }
        }
        return ['checked' => true, 'from_utc' => $from, 'until_utc' => $until, 'errors' => $errors];
    }
}
