<?php

declare(strict_types=1);

namespace {
    final class WP_Post
    {
        public function __construct(
            public int $ID,
            public string $post_title,
            public string $post_excerpt = 'Résumé public',
            public string $post_content = 'CONTENU_FICTIF_RESERVE_GARDE_B14'
        ) {
        }
    }
}

namespace Imagine\Site {
    function __(string $s, string $domain): string { return $s; }
    function esc_html(string $s): string { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }
    function esc_html__(string $s, string $domain): string { return esc_html($s); }
    function esc_attr(string $s): string { return esc_html($s); }
    function esc_url(string $s): string { return esc_html($s); }
    function get_the_title(\WP_Post $p): string { return $p->post_title; }
    function get_permalink(\WP_Post $p): string { return 'https://example.invalid/article/' . $p->ID; }
    function get_post_meta(int $id, string $key, bool $single): string { return '2026-10-15'; }
    function home_url(string $path): string { return 'https://example.invalid' . $path; }
    function get_terms(array $args): array { return []; }
    function get_the_post_thumbnail(\WP_Post $p, string $size, array $attr): string
    {
        return '<img src="https://example.invalid/fictif.png" alt="FICTIF" width="1" height="1" loading="'
            . $attr['loading'] . '" fetchpriority="' . $attr['fetchpriority'] . '">';
    }
    final class Navigation
    {
        public static function abonnementUrl(): string { return 'https://example.invalid/attente/'; }
    }
    final class Agenda
    {
        public static function groupes(): array { return ['futurs' => []]; }
    }
}

namespace Imagine\Theme {
    function imagine_issue_query(int $limit): object
    {
        return (object)['posts' => [new \WP_Post(1, 'Numéro FICTIF')]];
    }
    function imagine_issue_free_article(\WP_Post $p): ?\WP_Post
    {
        return new \WP_Post(2, 'Reportage public FICTIF');
    }
    function imagine_issue_product(int $id): string { return ''; }
    function imagine_partner_month(): void
    {
        echo '<section data-imagine-partenaire-mois="3"><p class="imagine-partnership-label">Partenariat</p><h2>Partenaire du mois</h2></section>';
    }
}
