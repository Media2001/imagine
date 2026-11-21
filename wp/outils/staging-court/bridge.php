<?php

declare(strict_types=1);

// Trusted local bridge, never loaded from the imported archive.
$path = getenv('A01_CONTEXT');
if ($path !== '/scratch/a01-context.json') {
    throw new RuntimeException('CONTEXTE_REFUSE');
}
$context = json_decode(file_get_contents($path), true, 32, JSON_THROW_ON_ERROR);
if (($context['wp_path'] ?? '') !== '/scratch/a01-site'
    || ($context['database'] ?? '') !== 'imagine_a01_staging'
    || !preg_match('/^[a-zA-Z0-9_]+_$/D', $context['prefix'] ?? '')) {
    throw new RuntimeException('CONTEXTE_REFUSE');
}
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=imagine_a01_staging;charset=utf8mb4', 'root', '');
if ((int) $pdo->query('SELECT @@skip_networking')->fetchColumn() !== 1) {
    throw new RuntimeException('RESEAU_REFUSE');
}
return [
    'context' => $context,
    'store' => new \Imagine\Staging\PdoStore($pdo, $context),
    'prefix' => $context['prefix'],
    'root' => $context['wp_path'],
    'probe' => static function () use ($context): array {
        require $context['wp_path'] . '/wp-load.php';
        return \Imagine\Staging\runtimeProbe();
    },
];
