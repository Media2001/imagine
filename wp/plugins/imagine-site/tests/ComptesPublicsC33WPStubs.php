<?php

declare(strict_types=1);

// Monde jetable C33 : aucune fonction d'écriture et aucun WordPress chargé.
$GLOBALS['c33_hooks'] = [];
$GLOBALS['c33_logged'] = false;
$GLOBALS['c33_author'] = false;
$GLOBALS['c33_feed'] = false;
$GLOBALS['c33_effects'] = [];
$GLOBALS['wp_query'] = new class {
    public function set_404(): void
    {
        $GLOBALS['c33_effects'][] = ['set_404'];
    }
};
function add_action(string $hook, mixed $callback, int $priority = 10, int $args = 1): void
{
    $GLOBALS['c33_hooks'][$hook][] = [$callback, $priority, $args];
}
function add_filter(string $hook, mixed $callback, int $priority = 10, int $args = 1): void
{
    add_action($hook, $callback, $priority, $args);
}
function remove_action(string $hook, mixed $callback, int $priority = 10): void
{
    $GLOBALS['c33_effects'][] = ['remove_action', $hook, $callback, $priority];
}
function is_user_logged_in(): bool
{
    return $GLOBALS['c33_logged'];
}
function is_author(): bool
{
    return $GLOBALS['c33_author'];
}
function is_feed(): bool
{
    return $GLOBALS['c33_feed'];
}
function status_header(int $status): void
{
    $GLOBALS['c33_effects'][] = ['status_header', $status];
}
function nocache_headers(): void
{
    $GLOBALS['c33_effects'][] = ['nocache_headers'];
}
function get_post(): mixed
{
    return null;
}
function get_bloginfo(string $key): string
{
    return 'SITE & FICTIF';
}
function get_query_var(string $key): string
{
    return 'atom';
}
function esc_html(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}
