<?php
/** Replay unchanged C08/C13 in rollback-only transactions on the named fake site. */
declare(strict_types=1);
namespace Imagine\Demo\C20Regressions;
define('IMAGINE_C20_READ_ONLY', true);
ob_start();
require __DIR__ . '/c20-native.php';
ob_end_clean();
\Imagine\Demo\C20\guard();
global $wpdb;
$tables = \Imagine\Demo\C20\tables();
$results = [];
foreach (['C08'=>'c08-runtime.php','C13'=>'c13-runtime.php'] as $lot=>$file) {
    $before = \Imagine\Demo\C20\fingerprint($tables);
    $wpdb->query('START TRANSACTION');
    $guard = static function (string $sql): string {
        if (preg_match('/^\s*(COMMIT|START\s+TRANSACTION|BEGIN|ROLLBACK|CREATE|ALTER|DROP|TRUNCATE|RENAME|LOCK\s+TABLE|UNLOCK\s+TABLE|SET\s+autocommit)\b/i', $sql)) {
            throw new \RuntimeException('C20 refuses transaction termination');
        }
        return $sql;
    };
    add_filter('query', $guard, PHP_INT_MAX);
    try {
        ob_start();
        (static function (string $path): void { require $path; })(__DIR__ . '/' . $file);
        $data = json_decode(ob_get_clean(), true, 512, JSON_THROW_ON_ERROR);
    } finally {
        remove_filter('query', $guard, PHP_INT_MAX);
        $wpdb->query('ROLLBACK');
        wp_cache_flush();
        \Imagine\Site\Paywall::invalidate();
    }
    $after = \Imagine\Demo\C20\fingerprint($tables);
    if ($after !== $before) {
        throw new \RuntimeException('C20 non-regression rollback drift');
    }
    $checks = $data['checks'] ?? $data;
    $results[$lot] = ['checks'=>$checks, 'total'=>count($checks), 'failures'=>array_keys(array_filter($checks, static fn ($ok)=>$ok!==true)), 'all_tables_rollback_exact'=>true];
}
wp_set_current_user(0);
echo wp_json_encode($results);
