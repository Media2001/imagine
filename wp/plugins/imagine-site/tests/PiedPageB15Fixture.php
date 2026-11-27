<?php

declare(strict_types=1);

namespace Imagine\Site;

const DAY_IN_SECONDS = 86400;
function __(string $text, string $domain): string { return $text; }
function esc_html__(string $text, string $domain): string { return $text; }
function esc_attr(string $text): string { return htmlspecialchars($text); }
function esc_url(string $text): string { return htmlspecialchars($text); }
function esc_html(string $text): string { return htmlspecialchars($text); }
function home_url(string $path): string { return 'https://example.invalid' . $path; }
function get_permalink(object $post): string { return 'https://example.invalid/numero/' . $post->ID; }
function get_the_title(object $post): string { return $post->post_title; }
function get_the_post_thumbnail(object $post, string $size, array $args): string { return '<img alt="FICTIF">'; }
function get_transient(string $key): mixed { return $GLOBALS['b15_cache'][$key] ?? false; }
function set_transient(string $key, mixed $value, int $ttl): bool { $GLOBALS['b15_cache'][$key] = $value; return true; }
function delete_transient(string $key): bool { unset($GLOBALS['b15_cache'][$key]); return true; }
function wp_nav_menu(array $args): void { echo '<ul><li><a href="/mentions/">Mentions FICTIF</a></li></ul>'; }
final class Accueil
{
    public static int $builds = 0;
    public static string $title = 'FICTIF Numéro A';
    public static function numero(): object
    {
        self::$builds++;
        return (object)['ID' => 42, 'post_title' => self::$title];
    }
}
final class Navigation
{
    public static function abonnementUrl(): string { return 'https://example.invalid/abonnement/'; }
}
