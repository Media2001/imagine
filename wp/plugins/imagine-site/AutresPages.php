<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Pages WordPress ordinaires : aucun éditeur ni type FAQ supplémentaire. */
final class AutresPages
{
    public const OPTION = 'imagine_b09_pages';

    public static function register(): void
    {
        add_action('after_setup_theme', static function (): void {
            register_nav_menu('imagine-footer', __('Navigation de pied de page', 'imagine-site'));
        });
        add_filter('the_content', static function (string $content): string {
            $pages = get_option(self::OPTION, []);
            if (
                is_singular('page') && in_the_loop() && is_main_query()
                && get_the_ID() === (int) ($pages['contact'] ?? 0)
            ) {
                return $content . Contact::formulaire();
            }
            return $content;
        }, 30);
    }
}
