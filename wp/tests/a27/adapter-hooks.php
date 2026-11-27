<?php

declare(strict_types=1);

// Isolated global native hook shell: declarations only, no WordPress bootstrap.
function add_filter(string $hook, callable $callback, int $priority = 10, int $args = 1): void
{
    $GLOBALS['a27_filters'][$priority][] = $callback;
}
function remove_filter(string $hook, callable $callback, int $priority = 10): void
{
    $GLOBALS['a27_filters'][$priority] = array_values(array_filter(
        $GLOBALS['a27_filters'][$priority] ?? [],
        static fn(callable $candidate): bool => $candidate !== $callback
    ));
    if (!$GLOBALS['a27_filters'][$priority]) {
        unset($GLOBALS['a27_filters'][$priority]);
    }
}
function apply_filters(string $hook, $value, $subscription)
{
    ksort($GLOBALS['a27_filters']);
    foreach ($GLOBALS['a27_filters'] as $callbacks) {
        foreach ($callbacks as $callback) {
            $value = $callback($value, $subscription);
        }
    }
    return $value;
}
