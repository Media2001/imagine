<?php

declare(strict_types=1);

namespace Imagine\Site;

// Doubles isolés : les métadonnées sont déséchappées comme par WordPress.
function get_option(string $key, mixed $default = false): mixed
{
    $GLOBALS['pv_reads'][$key] = ($GLOBALS['pv_reads'][$key] ?? 0) + 1;
    return $GLOBALS['pv_options'][$key] ?? $default;
}
function update_option(string $key, mixed $value, mixed $autoload = null): bool
{
    if ($key === ($GLOBALS['pv_option_failure'] ?? null)) { return false; }
    $GLOBALS['pv_options'][$key] = $value;
    return true;
}
function add_option(string $key, mixed $value, string $unused = '', mixed $autoload = null): bool
{
    if (isset($GLOBALS['pv_options'][$key])) { return false; }
    return update_option($key, $value, $autoload);
}
function delete_option(string $key): bool { unset($GLOBALS['pv_options'][$key]); return true; }
function wp_slash(mixed $value): mixed
{
    return is_array($value) ? array_map(__FUNCTION__, $value) : (is_string($value) ? addslashes($value) : $value);
}
function wp_unslash(mixed $value): mixed
{
    return is_array($value) ? array_map(__FUNCTION__, $value) : (is_string($value) ? stripslashes($value) : $value);
}
function wp_insert_post(array $data, bool $error = false): int
{
    $id = ++$GLOBALS['pv_next'];
    $GLOBALS['pv_posts'][$id] = (object) ['ID' => $id, 'post_type' => $data['post_type']];
    $GLOBALS['pv_meta'][$id] = wp_unslash($data['meta_input']);
    return $id;
}
function get_post(int $id): ?object { return $GLOBALS['pv_posts'][$id] ?? null; }
function get_post_type(int $id): mixed { return get_post($id)?->post_type ?? false; }
function get_post_meta(int $id, string $key, bool $single = true): mixed { return $GLOBALS['pv_meta'][$id][$key] ?? ''; }
function wp_delete_post(int $id, bool $force = false): mixed
{
    $GLOBALS['pv_deleted'][] = $id;
    if (in_array($id, $GLOBALS['pv_delete_fail'], true)) { return false; }
    $post = get_post($id);
    unset($GLOBALS['pv_posts'][$id], $GLOBALS['pv_meta'][$id]);
    return $post;
}
function is_wp_error(mixed $value): bool { return false; }
function __(string $text, string $domain): string { $GLOBALS['pv_translations'][] = [$text, $domain]; return $text; }
function esc_html(string $text): string { return htmlspecialchars($text, ENT_QUOTES, 'UTF-8'); }
function esc_attr(string $text): string { return esc_html($text); }
function esc_html__(string $text, string $domain): string { return esc_html(__($text, $domain)); }
