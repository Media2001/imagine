<?php

declare(strict_types=1);

// Isolated process: load the delivered helper, no WordPress, no alternate mapping.
function __($text, $domain): string { return $text; }
function add_filter(...$args): void { $GLOBALS['registered_hooks'][] = $args[0]; }
require dirname(__DIR__, 3) . '/themes/imagine/inc/catalogue.php';
$input = json_decode($argv[1], true, 512, JSON_THROW_ON_ERROR);
echo json_encode(['status' => Imagine\Theme\imagine_access_status($input),
    'hooks' => $GLOBALS['registered_hooks'] ?? []], JSON_THROW_ON_ERROR);
