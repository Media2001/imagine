<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Composition de l'accueil ; aucune règle d'accès ni donnée réservée réimplémentée. */
final class Accueil
{
    public static function register(): void
    {
        add_action('imagine_accueil', [self::class, 'rendre']);
    }

    public static function numero(): ?\WP_Post
    {
        $query = \Imagine\Theme\imagine_issue_query(1);
        return $query->posts[0] ?? null;
    }

    public static function libre(\WP_Post $issue): ?\WP_Post
    {
        $articles = get_posts(
            [
                'post_type' => 'post',
                'post_status' => 'publish',
                'numberposts' => -1,
                'meta_key' => 'imagine_numero_id',
                'meta_value' => $issue->ID,
                'orderby' => ['menu_order' => 'ASC', 'ID' => 'ASC'],
            ]
        );
        foreach ($articles as $article) {
            $status = \Imagine\Theme\imagine_access_status(Paywall::decisionListe($article));
            if ($status['code'] === 'libre') {
                return $article;
            }
        }
        return null;
    }

    public static function premiersEvenements(array $events): array
    {
        return array_values(array_slice($events, 0, 3));
    }

    private static function ouvrir(string $key, string $title): void
    {
        echo '<section' . ($key === 'thematiques' ? ' id="imagine-thematiques"' : '')
            . ' data-b14-section="' . esc_attr($key) . '" aria-labelledby="imagine-accueil-'
            . esc_attr($key) . '"><h2 id="imagine-accueil-' . esc_attr($key) . '">' . esc_html($title) . '</h2>';
    }

    public static function rendre(): void
    {
        $issue = self::numero();
        self::ouvrir('numero', __('Le numéro en cours', 'imagine-site'));
        if ($issue) {
            echo get_the_post_thumbnail($issue, 'medium', ['loading' => 'eager', 'fetchpriority' => 'high']);
            echo '<h3>' . esc_html(get_the_title($issue)) . '</h3><time datetime="'
                . esc_attr((string) get_post_meta($issue->ID, 'imagine_sortie', true)) . '">'
                . esc_html((string) get_post_meta($issue->ID, 'imagine_sortie', true)) . '</time><p>'
                . esc_html($issue->post_excerpt) . '</p>';
        } else {
            echo '<p>' . esc_html__('Aucun numéro publié.', 'imagine-site') . '</p>';
        }
        echo '</section>';
        self::ouvrir('conversion', __('Découvrir Imagine', 'imagine-site'));
        if ($issue) {
            echo '<p><a href="' . esc_url(get_permalink($issue)) . '">'
                . esc_html__('Découvrir le numéro', 'imagine-site') . '</a></p>';
            $buy = \Imagine\Theme\imagine_issue_product($issue->ID);
            if ($buy !== '') {
                echo '<p><a data-b14-acheter href="' . esc_url($buy) . '">'
                    . esc_html__('Acheter ce numéro', 'imagine-site') . '</a></p>';
            }
        }
        $subscribe = Navigation::abonnementUrl();
        if ($subscribe !== '') {
            echo '<p><a href="' . esc_url($subscribe) . '">' . esc_html__("S'abonner", 'imagine-site') . '</a></p>';
        }
        echo '</section>';
        $free = $issue ? self::libre($issue) : null;
        if ($free) {
            self::ouvrir('reportage', __('Reportage en accès libre', 'imagine-site'));
            echo '<a data-b14-reportage="' . esc_attr((string) $free->ID) . '" href="' . esc_url(get_permalink($free)) . '">'
                . esc_html(get_the_title($free))
                . get_the_post_thumbnail($free, 'medium', ['loading' => 'lazy', 'fetchpriority' => 'low']) . '</a></section>';
        }
        self::ouvrir('newsletter', __('Nos newsletters', 'imagine-site'));
        echo '<p><a href="' . esc_url(home_url('/nos-newsletters/')) . '">'
            . esc_html__('Découvrir nos newsletters', 'imagine-site') . '</a></p></section>';
        self::ouvrir('thematiques', __('Thématiques', 'imagine-site'));
        $terms = get_terms(['taxonomy' => 'imagine_thematique', 'hide_empty' => false]);
        echo '<ul>';
        foreach (is_array($terms) ? $terms : [] as $term) {
            $url = get_term_link($term);
            if (!is_wp_error($url)) {
                echo '<li><a href="' . esc_url($url) . '">' . esc_html($term->name) . '</a></li>';
            }
        }
        echo '</ul></section>';
        self::ouvrir('evenements', __('Événements à venir', 'imagine-site'));
        echo '<ul>';
        foreach (self::premiersEvenements(Agenda::groupes()['futurs']) as $event) {
            echo '<li data-b14-evenement="' . esc_attr((string) $event['id']) . '"><a href="'
                . esc_url(get_permalink($event['id'])) . '">' . esc_html($event['nom']) . '</a> — <time datetime="'
                . esc_attr($event['iso']) . '">' . esc_html($event['date']) . '</time></li>';
        }
        echo '</ul></section>';
        self::ouvrir('soutenir', __('Soutenir Imagine', 'imagine-site'));
        echo '<p><a href="' . esc_url(home_url('/soutenir/')) . '">' . esc_html__('Soutenir', 'imagine-site') . '</a></p></section>';
        self::ouvrir('cooperative', __('Notre coopérative', 'imagine-site'));
        echo '<p><a href="' . esc_url(home_url('/notre-cooperative/')) . '">'
            . esc_html__('Découvrir notre coopérative', 'imagine-site') . '</a></p></section>';
        \Imagine\Theme\imagine_partner_month();
    }
}
