<?php

declare(strict_types=1);

// Isolated process: load the delivered helper, no WordPress, no alternate mapping.
function __($text, $domain): string { return $text; }
function add_filter(...$args): void { $GLOBALS['registered_hooks'][] = $args[0]; }
// A local checkout contains its sibling theme. The canonical isolated T01
// harness copies Composer packages only; its documented read-only source mount
// remains /repo/wp. Read the actual delivered helper there, never a test copy.
$theme = dirname(__DIR__, 3) . '/themes/imagine/inc/catalogue.php';
if (!is_file($theme)) {
    $theme = '/repo/wp/themes/imagine/inc/catalogue.php';
}
if (!is_file($theme)) {
    throw new RuntimeException('Delivered Imagine catalogue helper is absent from the checkout/source mount.');
}
require $theme;
$input = json_decode($argv[1], true, 512, JSON_THROW_ON_ERROR);
echo json_encode(['status' => Imagine\Theme\imagine_access_status($input),
    'hooks' => $GLOBALS['registered_hooks'] ?? []], JSON_THROW_ON_ERROR);
