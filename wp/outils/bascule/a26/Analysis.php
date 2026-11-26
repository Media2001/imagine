<?php

declare(strict_types=1);

namespace Imagine\ThirdParties;

final class Analysis
{
    public const UNKNOWN = 'inconnu après neutralisation';
    public const FAMILIES = ['mesure', 'pixel', 'consentement', 'partage', 'carte', 'video', 'audio',
        'polices', 'formulaire_externe', 'anti_robot'];
    public const SERVICES = ['youtube', 'vimeo', 'dailymotion', 'soundcloud', 'spotify', 'mixcloud',
        'google_maps', 'openstreetmap', 'facebook', 'instagram', 'twitter', 'tiktok', 'autre'];

    private const PLUGINS = [
        'google-site-kit/google-site-kit.php' => 'mesure',
        'google-analytics-for-wordpress/googleanalytics.php' => 'mesure',
        'google-analytics-dashboard-for-wp/gadwp.php' => 'mesure',
        'wp-statistics/wp-statistics.php' => 'mesure',
        'matomo/matomo.php' => 'mesure',
        'facebook-for-woocommerce/facebook-for-woocommerce.php' => 'pixel',
        'facebook-pixel/facebook-for-wordpress.php' => 'pixel',
        'pixelyoursite/pixelyoursite.php' => 'pixel',
        'cookie-notice/cookie-notice.php' => 'consentement',
        'complianz-gdpr/complianz-gpdr.php' => 'consentement',
        'add-to-any/add-to-any.php' => 'partage',
        'wp-google-maps/wpGoogleMaps.php' => 'carte',
        'youtube-embed-plus/youtube.php' => 'video',
        'powerpress/powerpress.php' => 'audio',
        'use-any-font/use-any-font.php' => 'polices',
        'typeform/typeform.php' => 'formulaire_externe',
        'advanced-google-recaptcha/advanced-google-recaptcha.php' => 'anti_robot',
    ];
    private const HOSTS = [
        'youtube' => ['youtube.com', 'youtube-nocookie.com', 'youtu.be'],
        'vimeo' => ['vimeo.com'], 'dailymotion' => ['dailymotion.com', 'dai.ly'],
        'soundcloud' => ['soundcloud.com'], 'spotify' => ['spotify.com', 'spotify.link'],
        'mixcloud' => ['mixcloud.com'], 'google_maps' => ['maps.google.com', 'maps.google.fr'],
        'openstreetmap' => ['openstreetmap.org'], 'facebook' => ['facebook.com', 'fb.watch'],
        'instagram' => ['instagram.com'], 'twitter' => ['twitter.com', 'x.com'], 'tiktok' => ['tiktok.com'],
    ];

    public static function plugins(): array
    {
        return self::PLUGINS;
    }

    public static function decode(?string $raw): mixed
    {
        if ($raw === null) {
            return null;
        }
        set_error_handler(static function (): never {
            throw new \RuntimeException('A26_SETTINGS_UNREADABLE');
        });
        try {
            return unserialize($raw, ['allowed_classes' => false, 'max_depth' => 32]);
        } catch (\Throwable) {
            return null;
        } finally {
            restore_error_handler();
        }
    }

    private static function siteKitIdentifier(?string $raw): string
    {
        if ($raw === null) {
            return 'non';
        }
        $value = self::decode($raw);
        if (!is_array($value)) {
            return 'illisible';
        }
        $id = $value['measurementID'] ?? '';
        return is_string($id) ? (trim($id) === '' ? 'non' : 'oui') : 'illisible';
    }

    public static function families(array $active, ?string $settings, bool $neutralised, ?array $disabled): array
    {
        $out = [];
        $active = array_values(array_unique(array_filter($active, 'is_string')));
        foreach (self::FAMILIES as $family) {
            $paths = array_keys(self::PLUGINS, $family, true);
            $present = array_values(array_intersect($paths, $active));
            $count = count($present);
            $identifier = 'non';
            if ($count > 0) {
                // Only this exact official storage schema is qualified, not guessed option names.
                $supported = in_array('google-site-kit/google-site-kit.php', $present, true)
                    ? self::siteKitIdentifier($settings) : 'illisible';
                $singleSupported = $count === 1 && $present[0] === 'google-site-kit/google-site-kit.php';
                $identifier = $supported === 'oui' ? 'oui' : ($singleSupported ? $supported : 'illisible');
            }
            $affected = $neutralised && ($disabled === null
                ? in_array($family, ['mesure', 'pixel'], true)
                : count(array_intersect($paths, $disabled)) > 0);
            $out[$family] = ['active' => $affected ? self::UNKNOWN : $count,
                'identifier' => ($affected || ($neutralised && $count > 0)) ? self::UNKNOWN : $identifier];
        }
        return $out;
    }

    public static function services(array $urls, string $localHost): array
    {
        $found = [];
        foreach ($urls as $url) {
            if (!is_string($url)) {
                continue;
            }
            $url = html_entity_decode(trim($url), ENT_QUOTES | ENT_HTML5, 'UTF-8');
            $parsed = parse_url(str_starts_with($url, '//') ? 'https:' . $url : $url);
            if (!is_array($parsed) || !in_array(strtolower($parsed['scheme'] ?? ''), ['http', 'https'], true)
                || !isset($parsed['host']) || isset($parsed['user']) || isset($parsed['pass'])) {
                continue;
            }
            $host = strtolower(rtrim($parsed['host'], '.'));
            if ($host === strtolower(rtrim($localHost, '.'))) {
                continue;
            }
            $service = 'autre';
            $path = $parsed['path'] ?? '';
            if (in_array($host, ['google.com', 'www.google.com', 'google.fr', 'www.google.fr'], true)
                && ($path === '/maps' || str_starts_with($path, '/maps/'))) {
                $service = 'google_maps';
            } else {
                foreach (self::HOSTS as $label => $domains) {
                    foreach ($domains as $domain) {
                        if ($host === $domain || str_ends_with($host, '.' . $domain)) {
                            $service = $label;
                            break 2;
                        }
                    }
                }
            }
            $found[$service] = true;
        }
        return array_values(array_filter(self::SERVICES, static fn(string $s): bool => isset($found[$s])));
    }

    public static function htmlUrls(string $content): array
    {
        $urls = [];
        $content = preg_replace('~<(pre|code)\b[^>]*>.*?</\1\s*>|<!--.*?-->~is', '', $content) ?? '';
        $resourcePattern = '~<(iframe|embed|object|script|img|audio|video|source|link|blockquote)\b([^>]*)>~is';
        preg_match_all($resourcePattern, $content, $tags, PREG_SET_ORDER);
        foreach ($tags as $tag) {
            $attributePattern = '~\b(src|data-src|data|href|cite|data-instgrm-permalink)\s*=\s*'
                . '(?:"([^"]*)"|\x27([^\x27]*)\x27|([^\s>]+))~i';
            preg_match_all($attributePattern, $tag[2], $attrs, PREG_SET_ORDER);
            foreach ($attrs as $attr) {
                $key = strtolower($attr[1]);
                if (($key === 'href' && strtolower($tag[1]) !== 'link')
                    || ($key === 'data' && strtolower($tag[1]) !== 'object')) {
                    continue;
                }
                $urls[] = $attr[2] !== '' ? $attr[2] : (($attr[3] ?? '') !== '' ? $attr[3] : ($attr[4] ?? ''));
            }
        }
        // WordPress autoembeds standalone URLs. Ordinary inline links are not requests.
        preg_match_all('~(?:^|\n)\s*(https?://[^\s<>]+)\s*(?=\n|$)~i', $content, $bare);
        return [...$urls, ...$bare[1]];
    }

    public static function emptyCounts(): array
    {
        return array_fill_keys(self::SERVICES, 0);
    }

    public static function content(array $rows, bool $hasIssues, bool $neutralised): array|string
    {
        // The unchanged importer can blank an entire post_content containing a dangerous token.
        if ($neutralised) {
            return self::UNKNOWN;
        }
        $all = self::emptyCounts();
        $last = self::emptyCounts();
        $years = [];
        foreach ($rows as $row) {
            $year = is_int($row['year']) && $row['year'] >= 1000 && $row['year'] <= 9999 ? $row['year'] : 0;
            $years[$year] ??= self::emptyCounts();
            foreach (array_intersect(self::SERVICES, array_unique($row['services'])) as $service) {
                $all[$service]++;
                $years[$year][$service]++;
                if ($row['selected']) {
                    $last[$service]++;
                }
            }
        }
        ksort($years);
        $byYear = [];
        foreach ($years as $year => $counts) {
            $byYear[] = ['year' => $year, 'counts' => $counts];
        }
        return ['all' => $all, 'selection' => ['mode' => $hasIssues ? 'dix_derniers' : 'annee',
            'years' => $hasIssues ? [] : $byYear, 'last_ten' => $hasIssues ? $last : null]];
    }
}
