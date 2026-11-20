<?php

declare(strict_types=1);

// Harness-owned worker bridge. No wp-config read, no bootstrap before verifier's probe.
namespace Imagine\E2E;

$contextPath = getenv('E2E_CONTEXT') ?: '';
if (!preg_match('~^/scratch/context-(classic|hpos)\.json$~D', $contextPath)) {
    throw new \RuntimeException('Synthetic context required');
}
$context = json_decode(file_get_contents($contextPath), true, 32, JSON_THROW_ON_ERROR);
$database = $context['database'] ?? '';
$root = $context['wp_path'] ?? '';
if (!preg_match('/^imagine_e2e_(classic|hpos)_test$/D', $database)
    || !preg_match('~^/scratch/site-(classic|hpos)$~D', $root)) {
    throw new \RuntimeException('Only freshly generated throwaway fixtures are allowed');
}
$pdo = new \PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $database . ';charset=utf8mb4', 'root', '');
return [
    'context' => $context,
    'store' => new \Imagine\Staging\PdoStore($pdo, $context),
    'prefix' => 'wp_',
    'root' => $root,
    'probe' => static function () use ($root): array {
        require $root . '/wp-load.php';
        // Real probe, never synthetic all-true booleans. Missing WCS remains a blocker.
        return \Imagine\Staging\runtimeProbe();
    },
];
