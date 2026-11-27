<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Menu natif conservé ; complément public limité au titre, à l'image et au lien. */
final class Navigation
{
    public const NOMBRE = 'imagine_navigation_nombre';
    public const CACHE = 'imagine_b13_thematiques';

    public static function register(): void
    {
        add_filter('walker_nav_menu_start_el', [self::class, 'enrichir'], 10, 4);
        foreach (['save_post', 'deleted_post', 'set_object_terms', 'created_term', 'edited_term', 'delete_term'] as $hook) {
            add_action($hook, [self::class, 'invalider']);
        }
        foreach (['added_post_meta', 'updated_post_meta', 'deleted_post_meta'] as $hook) {
            add_action($hook, [self::class, 'invalider']);
        }
        add_action('update_option_' . self::NOMBRE, [self::class, 'invalider']);
        add_action('add_option_' . self::NOMBRE, [self::class, 'invalider']);
        add_action('admin_init', [self::class, 'reglages']);
        add_action(
            'admin_menu',
            static function (): void {
                add_options_page(
                    __('Menu principal', 'imagine-site'),
                    __('Menu principal', 'imagine-site'),
                    'manage_options',
                    'imagine-navigation',
                    [self::class, 'page']
                );
            }
        );
    }

    public static function nombre(mixed $value): int
    {
        return is_scalar($value) && preg_match('/^[0-9]+$/D', (string) $value)
            ? max(1, min(10, (int) $value)) : 3;
    }

    public static function reglages(): void
    {
        register_setting(
            'imagine_navigation',
            self::NOMBRE,
            ['type' => 'integer', 'default' => 3, 'sanitize_callback' => [self::class, 'nombre'], 'show_in_rest' => false]
        );
    }

    public static function page(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Réglage réservé à l’administration.', 'imagine-site'), '', ['response' => 403]);
        }
        echo '<div class="wrap"><h1>' . esc_html__('Menu principal', 'imagine-site') . '</h1>';
        echo '<form method="post" action="options.php">';
        settings_fields('imagine_navigation');
        echo '<label for="imagine-navigation-nombre">'
            . esc_html__('Articles récents par thématique (1 à 10)', 'imagine-site') . '</label> ';
        echo '<input id="imagine-navigation-nombre" type="number" min="1" max="10" name="'
            . esc_attr(self::NOMBRE) . '" value="' . esc_attr((string) self::nombre(get_option(self::NOMBRE, 3))) . '">';
        submit_button();
        echo '</form></div>';
    }

    public static function abonnementUrl(): string
    {
        $page = get_page_by_path('abonnement-en-attente');
        return $page && $page->post_status === 'publish' ? (string) get_permalink($page) : '';
    }

    public static function invalider(): void
    {
        delete_transient(self::CACHE);
    }

    public static function enrichir(string $html, object $item, int $depth, object $args): string
    {
        if (($args->theme_location ?? '') !== 'imagine-principal' || $depth !== 0
            || !in_array('imagine-nav-thematiques', (array) $item->classes, true)) {
            return $html;
        }
        return $html . self::thematiques();
    }

    public static function thematiques(): string
    {
        $cached = get_transient(self::CACHE);
        if (is_string($cached)) {
            return $cached;
        }
        $terms = get_terms(['taxonomy' => 'imagine_thematique', 'hide_empty' => false, 'orderby' => 'name']);
        if (is_wp_error($terms)) {
            return '';
        }
        $html = '<ul data-imagine-menu-etendu>';
        foreach ($terms as $term) {
            $url = get_term_link($term);
            if (is_wp_error($url)) {
                continue;
            }
            $html .= '<li data-b13-theme="' . esc_attr((string) $term->term_id) . '"><a href="'
                . esc_url($url) . '">' . esc_html($term->name) . '</a>';
            $posts = get_posts(
                [
                    'post_type' => 'post',
                    'post_status' => 'publish',
                    'post_password' => '',
                    'numberposts' => self::nombre(get_option(self::NOMBRE, 3)),
                    'orderby' => ['date' => 'DESC', 'ID' => 'DESC'],
                    'tax_query' => [['taxonomy' => 'imagine_thematique', 'terms' => $term->term_id]],
                ]
            );
            if ($posts) {
                $html .= '<ul>';
                foreach ($posts as $post) {
                    $html .= '<li data-b13-article="' . esc_attr((string) $post->ID) . '"><a href="'
                        . esc_url(get_permalink($post)) . '">' . esc_html(get_the_title($post));
                    $html .= get_the_post_thumbnail($post, 'thumbnail', ['loading' => 'lazy', 'fetchpriority' => 'low']);
                    $html .= '</a></li>';
                }
                $html .= '</ul>';
            }
            $html .= '</li>';
        }
        $html .= '</ul>';
        set_transient(self::CACHE, $html, DAY_IN_SECONDS);
        return $html;
    }
}
