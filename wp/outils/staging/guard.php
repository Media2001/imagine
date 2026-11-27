<?php

declare(strict_types=1);

namespace Imagine\Staging;

use RuntimeException;

final class Guard
{
    public static function context(array $context): string
    {
        if (
            ($context['environment'] ?? null) !== 'staging'
            || ($context['isolated'] ?? null) !== true
            || ($context['restored'] ?? null) !== true
            || !preg_match('/^[a-zA-Z0-9_]+_(staging|test)$/D', $context['database'] ?? '')
            || empty($context['production_hosts']) || !is_array($context['production_hosts'])
        ) {
            throw new RuntimeException('CONTEXTE_REFUSE');
        }
        $url = $context['target_url'] ?? '';
        $parts = parse_url($url);
        if (
            !is_array($parts) || !in_array($parts['scheme'] ?? '', ['http', 'https'], true)
            || isset($parts['user'], $parts['pass']) || isset($parts['user']) || isset($parts['query'])
            || isset($parts['fragment']) || !empty($parts['path'])
            || !preg_match('/^(localhost|[a-z0-9.-]+\.(test|localhost|invalid))$/D', $parts['host'] ?? '')
        ) {
            throw new RuntimeException('URL_REFUSEE');
        }
        foreach ($context['production_hosts'] as $host) {
            if (!is_string($host) || $host === '' || strtolower($parts['host']) === strtolower($host)) {
                throw new RuntimeException('PRODUCTION_REFUSEE');
            }
        }
        return $url;
    }
}
