<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Cinq zones publiques sans personnalisation ni géolocalisation. */
final class PiedPage
{
    public const CACHE = 'imagine_b15_numero';
    public const ZONES = ['abonnement', 'newsletter', 'numero', 'point-vente', 'mentions'];

    public static function register(): void
    {
        add_action('imagine_pied_page', [self::class, 'rendre']);
        foreach (['save_post_imagine_numero', 'save_post_attachment', 'deleted_post', 'added_post_meta', 'updated_post_meta', 'deleted_post_meta'] as $hook) {
            add_action($hook, [self::class, 'invalider']);
        }
        add_filter('nav_menu_css_class', [self::class, 'classes'], 10, 3);
        add_filter('nav_menu_link_attributes', [self::class, 'attributs'], 10, 3);
    }

    public static function invalider(): void
    {
        delete_transient(self::CACHE);
    }

    /** Ne change pas le menu stocké : seul le contexte courant du rendu est neutralisé. */
    public static function classes(array $classes, object $item, object $args): array
    {
        if (($args->theme_location ?? '') === 'imagine-footer') {
            $classes = array_values(array_filter($classes, static fn (string $name): bool => !preg_match('/^current[-_]/', $name)));
        }
        return $classes;
    }

    public static function attributs(array $attributes, object $item, object $args): array
    {
        if (($args->theme_location ?? '') === 'imagine-footer') {
            unset($attributes['aria-current']);
        }
        return $attributes;
    }

    public static function numero(): string
    {
        $cached = get_transient(self::CACHE);
        if (is_string($cached)) {
            return $cached;
        }
        $issue = Accueil::numero();
        $html = '';
        if ($issue) {
            $html = '<a data-b15-numero="' . esc_attr((string) $issue->ID) . '" href="'
                . esc_url(get_permalink($issue)) . '">'
                . get_the_post_thumbnail($issue, 'thumbnail', ['loading' => 'lazy', 'fetchpriority' => 'low'])
                . esc_html(get_the_title($issue)) . '</a>';
        }
        set_transient(self::CACHE, $html, DAY_IN_SECONDS);
        return $html;
    }

    public static function rendre(): void
    {
        $titles = [
            'abonnement' => __('Abonnement', 'imagine-site'),
            'newsletter' => __('Newsletter', 'imagine-site'),
            'numero' => __('Le numéro en cours', 'imagine-site'),
            'point-vente' => __('Point de vente', 'imagine-site'),
            'mentions' => __('Mentions', 'imagine-site'),
        ];
        foreach (self::ZONES as $zone) {
            echo '<section data-b15-zone="' . esc_attr($zone) . '" aria-labelledby="imagine-pied-'
                . esc_attr($zone) . '"><h2 id="imagine-pied-' . esc_attr($zone) . '">' . esc_html($titles[$zone]) . '</h2>';
            if ($zone === 'abonnement') {
                $url = Navigation::abonnementUrl();
                if ($url !== '') {
                    echo '<a href="' . esc_url($url) . '">' . esc_html__("S'abonner", 'imagine-site') . '</a>';
                }
            } elseif ($zone === 'newsletter') {
                echo '<a href="' . esc_url(home_url('/nos-newsletters/')) . '">'
                    . esc_html__('Nos newsletters', 'imagine-site') . '</a>';
            } elseif ($zone === 'numero') {
                echo self::numero();
            } elseif ($zone === 'point-vente') {
                echo '<a href="' . esc_url(home_url('/points-de-vente/')) . '">'
                    . esc_html__('Trouver un point de vente', 'imagine-site') . '</a>';
            } else {
                echo '<nav aria-label="' . esc_attr__('Navigation de pied de page', 'imagine-site') . '">';
                if (has_nav_menu('imagine-footer')) {
                    wp_nav_menu(
                        [
                            'theme_location' => 'imagine-footer',
                            'container' => false,
                            'fallback_cb' => false,
                        ]
                    );
                }
                echo '</nav>';
            }
            echo '</section>';
        }
    }
}
