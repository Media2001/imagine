<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Temporary consent lock at native resolution boundaries; never edits post_content. */
final class IntegrationsCorps
{
    public static function register(): void
    {
        // First native handler: runs BEFORE persisted _oembed_* HTML and provider handlers.
        wp_embed_register_handler('imagine_corps_externe', '~^(?:https?:)?//~i', [self::class, 'lien'], PHP_INT_MIN);
        add_filter('pre_oembed_result', [self::class, 'resolution'], PHP_INT_MAX, 2);
        add_filter('pre_render_block', [self::class, 'bloc'], PHP_INT_MAX, 2);
        // The proxy calls get_data(), NOT get_html(); pre_oembed_result alone is insufficient.
        // This boundary also precedes the proxy's transient cache.
        add_filter('rest_dispatch_request', [self::class, 'apercu'], PHP_INT_MAX, 3);
    }

    public static function externe(string $url): bool
    {
        $target = wp_parse_url($url);
        if (!is_array($target) || empty($target['host']) || isset($target['user']) || isset($target['pass'])) {
            return true;
        }
        foreach ([home_url('/'), site_url('/')] as $base) {
            $local = wp_parse_url($base);
            $scheme = strtolower($target['scheme'] ?? $local['scheme']);
            $port = $target['port'] ?? ($scheme === 'https' ? 443 : 80);
            $localPort = $local['port'] ?? (strtolower($local['scheme']) === 'https' ? 443 : 80);
            $path = $target['path'] ?? '/';
            $root = rtrim($local['path'] ?? '/', '/');
            if (strtolower($target['host']) === strtolower($local['host'])
                && $scheme === strtolower($local['scheme']) && $port === $localPort
                && ($path === $root || str_starts_with($path, $root . '/'))
            ) {
                return false;
            }
        }
        return true;
    }

    private static function html(string $url): string
    {
        return '<a href="' . esc_url($url, ['http', 'https']) . '">' . esc_html($url) . '</a>';
    }

    /** Returning false delegates same-site embeds to the native pipeline unchanged. */
    public static function lien(array $matches, array $attributes, string $url): string|false
    {
        return self::externe($url) ? self::html($url) : false;
    }

    public static function resolution(mixed $result, string $url): mixed
    {
        return self::externe($url) ? self::html($url) : $result;
    }

    public static function bloc(?string $rendered, array $block): ?string
    {
        $url = $block['attrs']['url'] ?? null;
        if (($block['blockName'] ?? '') === 'core/embed' && is_string($url) && self::externe($url)) {
            return '<p>' . self::html($url) . '</p>';
        }
        return $rendered;
    }

    public static function apercu(mixed $response, \WP_REST_Request $request, string $route): mixed
    {
        $url = $request->get_param('url');
        if (rtrim($request->get_route(), '/') !== '/oembed/1.0/proxy'
            || !is_string($url) || !self::externe($url)
            || is_wp_error($response) || !current_user_can('edit_posts')
        ) {
            return $response;
        }
        // A link result supplies the editor's ordinary link without preview assets.
        return new \WP_REST_Response(['version' => '1.0', 'type' => 'link', 'html' => self::html($url)], 200);
    }
}
