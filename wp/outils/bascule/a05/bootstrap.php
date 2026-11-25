<?php

/** Load the unchanged A04 command guards; discard bootstrap SQL mutations. */
declare(strict_types=1);

namespace Imagine\Nettoyage;

require_once dirname(__DIR__) . '/a04/bootstrap.php';
$GLOBALS['imagine_a05_writes'] = false;
add_filter('query', static function (string $query): string {
    if (!$GLOBALS['imagine_a05_writes'] && !preg_match('/\A\s*(?:SELECT|SHOW|DESCRIBE|EXPLAIN|SET)\b/i', $query)) {
        return 'SELECT 0';
    }
    return $query;
}, PHP_INT_MAX);
