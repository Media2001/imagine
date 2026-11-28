<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Ferme les voies de comptes anonymes, sans changer les permissions éditoriales. */
final class ComptesPublics
{
    public static function register(): void
    {
        add_action('template_redirect', [self::class, 'auteur'], 0);
        add_filter('rest_pre_dispatch', [self::class, 'rest'], 100, 3);
        add_filter('wp_sitemaps_add_provider', [self::class, 'sitemap'], 100, 2);
        add_filter('the_author', [self::class, 'auteurFlux'], 100);
        add_filter('get_the_author_user_url', [self::class, 'adresseFlux'], 100);
        add_filter('oembed_response_data', [self::class, 'oembed'], 100, 4);
    }

    public static function auteur(): void
    {
        if (is_user_logged_in() || !is_author()) {
            return;
        }
        global $wp_query;
        $wp_query->set_404();
        status_header(404);
        nocache_headers();
        // La redirection native ?author=ID -> /author/login/ ne doit pas s'exécuter.
        remove_action('template_redirect', 'redirect_canonical');
    }

    public static function rest(mixed $result, \WP_REST_Server $server, \WP_REST_Request $request): mixed
    {
        if (!is_user_logged_in() && ComptesPublicsRegles::utilisateurs($request->get_route())) {
            return new \WP_Error('rest_no_route', __('Aucune route ne correspond à cette adresse.', 'imagine-site'), ['status' => 404]);
        }
        return $result;
    }

    public static function sitemap(mixed $provider, string $name): mixed
    {
        return !is_user_logged_in() && $name === 'users' ? false : $provider;
    }

    private static function signature(\WP_Post $post): string
    {
        return ComptesPublicsRegles::signature(get_post_meta($post->ID, PageArticle::SIGNATURE, true), get_bloginfo('name'));
    }

    public static function auteurFlux(string $author): string
    {
        if (is_user_logged_in() || !is_feed()) {
            return $author;
        }
        $post = get_post();
        $name = $post ? self::signature($post) : get_bloginfo('name');
        // RSS2 place la valeur dans CDATA ; Atom attend une chaîne XML échappée.
        return get_query_var('feed') === 'rss2'
            ? str_replace(']]>', ']]]]><![CDATA[>', $name)
            : esc_html($name);
    }

    public static function adresseFlux(string $url): string
    {
        return !is_user_logged_in() && is_feed() ? '' : $url;
    }

    public static function oembed(array $data, \WP_Post $post, int $width, int $height): array
    {
        if (is_user_logged_in()) {
            return $data;
        }
        $data['author_name'] = self::signature($post);
        unset($data['author_url']);
        return $data;
    }
}
