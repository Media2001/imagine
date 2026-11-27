<?php

declare(strict_types=1);

function home_url(string $path = ''): string { return 'https://demo.example.invalid/magazine' . $path; }
function site_url(string $path = ''): string { return 'https://demo.example.invalid/magazine/wp' . $path; }
function wp_parse_url(string $url): array|false { return parse_url($url); }
function esc_url(string $url, array $protocols = []): string { return preg_match('~^(?:https?:)?//~i', $url) ? htmlspecialchars($url, ENT_QUOTES) : ''; }
function esc_html(string $value): string { return htmlspecialchars($value, ENT_QUOTES); }
function current_user_can(string $cap): bool { return $GLOBALS['b12_editor'] ?? true; }
function is_wp_error(mixed $value): bool { return $value instanceof WP_Error; }
function add_filter(string $name, callable $callback, int $priority, int $args): void { $GLOBALS['b12_hooks'][$name] = [$callback, $priority, $args]; }
function wp_embed_register_handler(string $id, string $regex, callable $callback, int $priority): void { $GLOBALS['b12_handler'] = [$id, $regex, $callback, $priority]; }
final class WP_Error {}
final class WP_REST_Request
{
    public function __construct(private string $route, private mixed $url) {}
    public function get_route(): string { return $this->route; }
    public function get_param(string $name): mixed { return $this->url; }
}
final class WP_REST_Response
{
    public function __construct(public array $data, public int $status) {}
}
