<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Pages natives vides : seuls les raccords de navigation sont générés. */
final class Cooperative
{
    public const OPTION = 'imagine_b08_pages';

    public static function register(): void
    {
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
