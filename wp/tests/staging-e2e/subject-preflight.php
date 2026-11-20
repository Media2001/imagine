<?php

declare(strict_types=1);

namespace Imagine\E2E;

require '/subject/lib.php';
require '/subject/pdo-store.php';
require '/subject/files.php';
$worker = require '/opt/e2e/worker-bridge.php';
$store = $worker['store'];
$schema = $store->schema();
$catalogue = require '/subject/schema.php';
$mismatches = [];
foreach ($schema as $table => $columns) {
    $kind = str_starts_with($table, 'wp_') ? substr($table, 3) : '';
    if (!isset($catalogue[$kind])) {
        $mismatches[$table] = ['unknown_table' => true];
    } elseif ($extra = array_values(array_diff($columns, explode(' ', $catalogue[$kind])))) {
        $mismatches[$table] = ['unknown_columns' => $extra];
    }
}
try {
    $engine = new \Imagine\Staging\Engine($store, $worker['context'], $worker['prefix']);
    $files = new \Imagine\Staging\Files($worker['root']);
    $result = ['guard_ok' => true, 'schema_mismatches' => $mismatches];
    if (getenv('E2E_PREFLIGHT_PHASE') === 'neutraliser-diagnostic') {
        $files->purge();
        $engine->neutraliser();
        $result['diagnostic_retry'] = 'completed';
    }
    if (getenv('E2E_PREFLIGHT_PHASE') === 'data') {
        $result['data_report'] = $engine->verifier(null); // Deliberately no runtime proof.
        $scrub = new \ReflectionMethod($engine, 'scrub');
        $locations = [];
        foreach ($schema as $table => $_) {
            foreach ($store->rows($table) as $row) {
                foreach ($row as $column => $value) {
                    if (is_string($value) && (\Imagine\Staging\Engine::dangerous($value)
                        || $scrub->invoke(null, $value, false, 0) !== $value)) {
                        $locations[$table . '.' . $column] = true;
                    }
                }
            }
        }
        $result['noncanonical_or_secret_columns'] = array_keys($locations);
    }
} catch (\Throwable $exception) {
    $code = $exception->getMessage();
    $metadataMentions = [];
    if ($exception instanceof \PDOException) {
        $privateMessage = (string) ($exception->errorInfo[2] ?? '');
        foreach ($schema as $table => $columns) {
            foreach ($columns as $column) {
                if (str_contains($privateMessage, '`' . $table . '`')
                    || str_contains($privateMessage, "'" . $column . "'")) {
                    $metadataMentions[$table . '.' . $column] = true;
                }
            }
        }
    }
    $result = ['guard_ok' => false, 'metadata_mentions' => array_keys($metadataMentions), 'schema_mismatches' => $mismatches,
        'refusal_tag' => preg_match('/^[A-Z_]+$/D', $code) ? $code : 'REDACTED_REFUSAL',
        'exception_class' => get_class($exception),
        'sqlstate' => $exception instanceof \PDOException ? ($exception->errorInfo[0] ?? null) : null,
        'driver_errno' => $exception instanceof \PDOException ? ($exception->errorInfo[1] ?? null) : null,
        'source_file' => basename($exception->getFile()),
        'source_line' => $exception->getLine(),
        'functions' => array_values(array_filter(array_column($exception->getTrace(), 'function'),
            static fn (string $function): bool => (bool) preg_match('/^[A-Za-z_][A-Za-z0-9_]*$/D', $function)))];
}
echo 'E2E_JSON=' . json_encode($result, JSON_THROW_ON_ERROR) . "\n";
