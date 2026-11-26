<?php

declare(strict_types=1);

namespace Imagine\ThirdParties;

final class Inventory
{
    private const SHORTCODES = ['embed', 'video', 'audio', 'youtube', 'vimeo', 'dailymotion',
        'soundcloud', 'spotify', 'mixcloud', 'googlemaps', 'google_maps'];

    private static function rows(string $sql, array $args = []): array
    {
        global $wpdb;
        $rows = $wpdb->get_results($args ? $wpdb->prepare($sql, ...$args) : $sql, ARRAY_A);
        if (!is_array($rows) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A26_QUERY_FAILED');
        }
        return $rows;
    }

    private static function option(string $name): array
    {
        global $wpdb;
        $rows = self::rows("SELECT option_value FROM {$wpdb->options} WHERE BINARY option_name=BINARY %s", [$name]);
        if (count($rows) > 1) {
            throw new \RuntimeException('A26_QUERY_FAILED');
        }
        return $rows;
    }

    private static function urls(string $content, array $seen = [], int $depth = 0): array
    {
        global $wpdb;
        if ($depth > 16 || strlen($content) > 4194304) {
            throw new \RuntimeException('A26_CONTENT_UNSUPPORTED');
        }
        $urls = Analysis::htmlUrls($content);
        // No callback, render, oEmbed request, or shortcode expansion is invoked.
        preg_match_all('/' . get_shortcode_regex(self::SHORTCODES) . '/s', $content, $shortcodes, PREG_SET_ORDER);
        foreach ($shortcodes as $shortcode) {
            if ($shortcode[1] === '[' && $shortcode[6] === ']') {
                continue;
            }
            $atts = shortcode_parse_atts($shortcode[3]);
            foreach (is_array($atts) ? $atts : [] as $key => $value) {
                if (in_array($key, ['src', 'url', 'mp3', 'mp4', 'webm', 'ogg', 'm4a'], true) && is_string($value)) {
                    $urls[] = $value;
                }
            }
            $body = trim($shortcode[5] ?? '');
            if (preg_match('~\Ahttps?://[^\s<>]+\z~i', $body)) {
                $urls[] = $body;
            }
        }
        // Use the native default parser directly, not the replaceable block_parser_class filter.
        $parser = new \WP_Block_Parser();
        $walk = static function (array $blocks) use (&$walk, &$urls, $seen, $depth, $wpdb): void {
            foreach ($blocks as $block) {
                $name = $block['blockName'] ?? null;
                $attrs = $block['attrs'] ?? [];
                if (in_array($name, ['core/embed', 'core/audio', 'core/video', 'core/image'], true)) {
                    foreach (['url', 'src'] as $key) {
                        if (is_string($attrs[$key] ?? null)) {
                            $urls[] = $attrs[$key];
                        }
                    }
                }
                if ($name === 'core/block') {
                    $id = $attrs['ref'] ?? null;
                    if (!is_int($id) || $id < 1 || in_array($id, $seen, true)) {
                        throw new \RuntimeException('A26_CONTENT_UNSUPPORTED');
                    }
                    $rows = self::rows("SELECT post_content FROM {$wpdb->posts} WHERE ID=%d AND post_type='wp_block' AND post_status='publish'", [$id]);
                    if (count($rows) !== 1) {
                        throw new \RuntimeException('A26_CONTENT_UNSUPPORTED');
                    }
                    $urls = [...$urls, ...self::urls($rows[0]['post_content'], [...$seen, $id], $depth + 1)];
                }
                $walk($block['innerBlocks'] ?? []);
            }
        };
        $walk($parser->parse($content));
        return $urls;
    }

    public static function collect(string $site, ?array $mapping = null): array
    {
        foreach (['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
            'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook) {
            $GLOBALS['wp_filter'][$hook][PHP_INT_MAX][] = ['function' => static fn(): int => 0, 'accepted_args' => 0];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        global $wpdb;
        $storage = \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled() ? 'hpos' : 'classic';
        $activeRaw = self::option('active_plugins');
        $active = Analysis::decode($activeRaw[0]['option_value'] ?? null);
        if (!is_array($active) || !array_is_list($active) || count(array_filter($active, 'is_string')) !== count($active)) {
            throw new \RuntimeException('A26_QUERY_FAILED');
        }
        $marker = self::option('imagine_staging_disabled_plugins');
        $neutralised = $marker !== [];
        $disabled = Analysis::decode($marker[0]['option_value'] ?? null);
        $disabled = is_array($disabled) && array_is_list($disabled)
            && count(array_filter($disabled, 'is_string')) === count($disabled) ? $disabled : null;
        $settings = self::option('googlesitekit_analytics-4_settings');
        $families = Analysis::families($active, $settings[0]['option_value'] ?? null, $neutralised, $disabled);
        $rows = [];
        if (!$neutralised) {
            $selected = $mapping === null ? [] : Issues::select($wpdb, $mapping);
            $types = array_values(array_diff(get_post_types(['public' => true]), ['attachment', 'wp_block']));
            if ($mapping !== null && !in_array($mapping['article_type'], $types, true)) {
                throw new \RuntimeException('A26_MAPPING_INVALID');
            }
            $local = self::option('home');
            $localHost = parse_url($local[0]['option_value'] ?? '', PHP_URL_HOST);
            if (!is_string($localHost)) {
                throw new \RuntimeException('A26_QUERY_FAILED');
            }
            foreach ($types as $type) {
                $posts = self::rows("SELECT ID,post_date_gmt,post_content FROM {$wpdb->posts} WHERE post_status='publish' AND post_type=%s ORDER BY ID", [$type]);
                foreach ($posts as $post) {
                    $year = preg_match('/\A([1-9][0-9]{3})-[0-9]{2}-[0-9]{2}/D', $post['post_date_gmt'], $m) ? (int) $m[1] : 0;
                    $rows[] = ['year' => $year, 'services' => Analysis::services(self::urls($post['post_content']), $localHost),
                        'selected' => in_array((int) $post['ID'], $selected, true)];
                }
            }
        }
        return ['schema' => 'imagine-a26-third-parties-v1', 'read_only' => true, 'storage' => $storage,
            'neutralisation' => $neutralised ? Analysis::UNKNOWN : 'observe', 'families' => $families,
            'content' => Analysis::content($rows, $mapping !== null, $neutralised)];
    }
}
