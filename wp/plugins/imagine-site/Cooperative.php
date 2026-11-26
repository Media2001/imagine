<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Pages natives vides : seuls les raccords de navigation sont générés. */
final class Cooperative
{
    public const OPTION = 'imagine_b08_pages';

    public static function register(): void
    {
        add_action('after_setup_theme', static function (): void {
            register_nav_menu('imagine-principal', __('Navigation principale', 'imagine-site'));
        });
        add_filter('wp_nav_menu_items', static function (string $html, $args): string {
            if (($args->theme_location ?? '') !== 'imagine-principal') {
                return $html;
            }
            $tags = new \WP_HTML_Tag_Processor($html);
            while ($tags->next_tag('LI')) {
                foreach (['kiosque', 'agenda', 'compte'] as $key) {
                    if ($tags->has_class('imagine-nav-' . $key)) {
                        $tags->set_attribute('data-imagine-nav', $key);
                    }
                }
            }
            return $tags->get_updated_html();
        }, 10, 2);
        add_filter('the_content', static function (string $content): string {
            if (!is_singular('page') || !in_the_loop() || !is_main_query()) {
                return $content;
            }
            return self::rendre((int)get_the_ID(), $content);
        }, 30);
    }

    public static function rendre(int $id, string $content): string
    {
        $pages = get_option(self::OPTION, []);
        if ($id === (int)($pages['soutenir'] ?? 0)) {
            return $content . Soutenir::rendre();
        }
        if ($id === (int)($pages['sujet'] ?? 0)) {
            return $content . Sujet::formulaire();
        }
        $root = (int)($pages['cooperative'] ?? 0);
        if ($id === $root && $root > 0) {
            $html = '<nav aria-label="' . esc_attr(__('Notre coopérative', 'imagine-site')) . '"><ul>';
            foreach (CooperativeRegles::PAGES as $slug => $title) {
                $child = (int)($pages['enfants'][$slug] ?? 0);
                if ($child > 0) {
                    $html .= '<li><a href="' . esc_url(get_permalink($child)) . '">' . esc_html(__($title, 'imagine-site')) . '</a></li>';
                }
            }
            $space = get_page_by_path('espace-cooperateurs');
            if ($space) {
                $html .= '<li><a href="' . esc_url(get_permalink($space->ID)) . '">' . esc_html(__('Espace coopérateurs', 'imagine-site')) . '</a></li>';
            }
            $html .= '</ul></nav>';
            if (!empty($pages['sujet'])) {
                $html .= '<p><a href="' . esc_url(get_permalink((int)$pages['sujet'])) . '">' . esc_html(__('Proposer un sujet', 'imagine-site')) . '</a></p>';
            }
            return $content . $html;
        }
        if ($root > 0 && in_array($id, array_map('intval', $pages['enfants'] ?? []), true)) {
            return $content . '<p><a href="' . esc_url(get_permalink($root)) . '">' . esc_html(__('Notre coopérative', 'imagine-site')) . '</a></p>';
        }
        return $content;
    }
}
