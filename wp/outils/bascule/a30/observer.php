<?php

declare(strict_types=1);

namespace Imagine\OfflineDryRun;

ini_set('display_errors', '0');
ini_set('log_errors', '0');
set_error_handler(static function (int $severity): bool {
    if (error_reporting() & $severity) {
        throw new \RuntimeException('A30_INVENTORY_FAILED');
    }
    return true;
});
$level = ob_get_level();
ob_start();
try {
    if (PHP_SAPI !== 'cli' || getenv('A30_CONFINED') !== '1' || function_exists('mail') || function_exists('exec')) {
        throw new \RuntimeException('A30_CONFINEMENT_REQUIRED');
    }
    $options = [];
    foreach (array_slice($argv, 1) as $argument) {
        if (!preg_match('/\A--(wp-path|output)=(.+)\z/D', $argument, $m) || isset($options[$m[1]])) {
            throw new \RuntimeException('A30_USAGE');
        }
        $options[$m[1]] = $m[2];
    }
    if (count($options) !== 2) {
        throw new \RuntimeException('A30_USAGE');
    }
    $raw = stream_get_contents(STDIN, 16777217);
    if ($raw === false || strlen($raw) > 16777216) {
        throw new \RuntimeException('A30_INPUT_INVALID');
    }
    $input = json_decode($raw, true, 64, JSON_THROW_ON_ERROR);
    if (!is_array($input) || array_keys($input) !== ['a13_code', 'rows']
        || !in_array($input['a13_code'], [0, 1], true) || !is_array($input['rows'])) {
        throw new \RuntimeException('A30_INPUT_INVALID');
    }
    $last = 1;
    foreach ($input['rows'] as $row) {
        if (!is_array($row) || array_keys($row) !== ['line', 'rejected', 'email', 'product', 'payment']
            || !is_int($row['line']) || $row['line'] <= $last || !is_bool($row['rejected'])
            || !is_string($row['email']) || strlen($row['email']) > 254
            || ($row['product'] !== null && (!is_int($row['product']) || $row['product'] < 1))
            || !in_array($row['payment'], ['virement', 'domiciliation_papier', 'autre'], true)) {
            throw new \RuntimeException('A30_INPUT_INVALID');
        }
        $last = $row['line'];
    }
    require dirname(__DIR__) . '/a12/AuditLibrary.php';
    \Imagine\ContentInventory\AuditLibrary::load();
    require dirname(__DIR__) . '/a11/Runtime.php';
    require __DIR__ . '/Analysis.php';
    require __DIR__ . '/Inventory.php';
    $result = Inventory::collect($options['wp-path'], $input['rows']);
    $file = $options['output'] . '/result.json';
    $handle = fopen($file, 'xb');
    if (!$handle || !chmod($file, 0600)) {
        throw new \RuntimeException('A30_INVENTORY_FAILED');
    }
    $json = json_encode($result, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE) . "\n";
    if (fwrite($handle, $json) !== strlen($json)) {
        throw new \RuntimeException('A30_INVENTORY_FAILED');
    }
    fclose($handle);
    while (ob_get_level() > $level) {
        ob_end_clean();
    }
    fwrite(STDOUT, 'A30_OK ' . hash('sha256', $json) . "\n");
    exit(0);
} catch (\Throwable $error) {
    while (ob_get_level() > $level) {
        ob_end_clean();
    }
    $allowed = ['A30_USAGE', 'A30_CONFINEMENT_REQUIRED', 'A30_INPUT_INVALID', 'A30_QUERY_FAILED',
        'A30_EXISTING_EMAIL_AMBIGUOUS', 'A30_NATIVE_UNSUPPORTED', 'A30_INVENTORY_FAILED',
        'A11_CONFIG_UNSAFE', 'A11_CONFIG_OVERRIDE_UNSUPPORTED', 'A11_DROPIN_UNSUPPORTED',
        'A11_SYMLINK_UNSUPPORTED', 'A11_HOME_INVALID', 'A11_MULTISITE_UNSUPPORTED'];
    $code = in_array($error->getMessage(), $allowed, true) ? $error->getMessage() : 'A30_INVENTORY_FAILED';
    $message = class_exists(\Imagine\PublicAddresses\Runtime::class)
        ? \Imagine\PublicAddresses\Runtime::refusalMessage($error, $code) : $code;
    fwrite(STDERR, $message . "\n");
    exit(1);
}
