<?php

declare(strict_types=1);

namespace Imagine\Theme;

if (!defined('ABSPATH')) {
    exit;
}

function imagine_setup(): void
{
    load_theme_textdomain('imagine', get_template_directory() . '/languages');
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', ['search-form', 'gallery', 'caption', 'style', 'script']);
}
add_action('after_setup_theme', __NAMESPACE__ . '\\imagine_setup');

function imagine_styles(): void
{
    foreach (['imagine-tokens' => '/assets/tokens.css', 'imagine-structure' => '/style.css'] as $handle => $path) {
        wp_enqueue_style(
            $handle,
            get_template_directory_uri() . $path,
            $handle === 'imagine-structure' ? ['imagine-tokens'] : [],
            (string) filemtime(get_template_directory() . $path)
        );
    }
}
add_action('wp_enqueue_scripts', __NAMESPACE__ . '\\imagine_styles');

/** Unique sortie du corps des articles. C-08 modifiera ce point, pas les gabarits. */
function imagine_article_body(): void
{
    $post = get_post();
    if ($post && class_exists('Imagine\\Site\\Paywall') && \Imagine\Site\Paywall::managed($post)) {
        $decision = \Imagine\Site\Paywall::decision($post);
        echo '<div class="imagine-paywall-body">';
        if ($decision['complet']) {
            the_content();
        } else {
            echo '<p>' . esc_html(\Imagine\Site\Paywall::excerpt($post)) . '</p>';
        }
        echo '</div>';
        if (in_array($decision['bloc'], ['abonnement', 'connexion', 'regularisation', 'decouverte_epuisee'], true)) {
            get_template_part('parts/paywall', $decision['bloc'], $decision);
        }
        return;
    }
    // Repli B00 si le plugin C08 n'est pas chargé : verrou natif conservé en base.
    if (post_password_required()) {
        echo get_the_password_form();
        return;
    }
    the_content();
}

/** La date éditoriale, et non la date d'import, ordonne les numéros. */
function imagine_archive_order(\WP_Query $query): void
{
    if (is_admin() || !$query->is_main_query()) {
        return;
    }
    if ($query->is_post_type_archive('imagine_numero')) {
        $query->set('meta_key', 'imagine_sortie');
        $query->set('orderby', ['meta_value' => 'DESC', 'ID' => 'DESC']);
        $query->set('posts_per_page', -1);
    } elseif ($query->is_post_type_archive('imagine_evenement')) {
        $query->set('meta_key', 'imagine_date');
        $query->set('orderby', ['meta_value' => 'ASC', 'ID' => 'ASC']);
    }
}
add_action('pre_get_posts', __NAMESPACE__ . '\\imagine_archive_order');

function imagine_issue_query(int $limit = -1): \WP_Query
{
    return new \WP_Query([
        'post_type' => 'imagine_numero', 'post_status' => 'publish',
        'posts_per_page' => $limit, 'meta_key' => 'imagine_sortie',
        'orderby' => ['meta_value' => 'DESC', 'ID' => 'DESC'],
    ]);
}

/** Cartes sémantiques sans corps d'article, y compris en recherche. */
function imagine_list(\WP_Query $query, int $heading = 2, bool $covers = false): void
{
    $tag = $heading === 3 ? 'h3' : 'h2';
    if (!$query->have_posts()) {
        echo '<p>' . esc_html__('Aucun contenu pour le moment.', 'imagine') . '</p>';
        return;
    }
    echo '<ul class="imagine-list">';
    while ($query->have_posts()) {
        $query->the_post();
        echo '<li data-imagine-id="' . esc_attr((string) get_the_ID()) . '">';
        echo '<' . $tag . '><a href="' . esc_url(get_permalink()) . '">' . esc_html(get_the_title()) . '</a></' . $tag . '>';
        if ($covers) {
            echo '<div class="imagine-cover">' . get_the_post_thumbnail(get_the_ID(), 'medium') . '</div>';
            imagine_date('imagine_sortie');
        } elseif (get_post_type() === 'imagine_evenement') {
            imagine_date('imagine_date');
        }
        echo '<p>' . esc_html(get_the_excerpt()) . '</p></li>';
    }
    echo '</ul>';
    wp_reset_postdata();
}

function imagine_date(string $key): void
{
    $date = (string) get_post_meta(get_the_ID(), $key, true);
    if ($date !== '') {
        echo '<p><time datetime="' . esc_attr($date) . '">' . esc_html($date) . '</time></p>';
    }
}

function imagine_navigation(): void
{
    $links = [
        home_url('/') => __('Accueil', 'imagine'),
        get_post_type_archive_link('imagine_numero') ?: home_url('/') => __('Kiosque', 'imagine'),
        home_url('/#imagine-thematiques') => __('Thématiques', 'imagine'),
        get_post_type_archive_link('imagine_evenement') ?: home_url('/') => __('Agenda', 'imagine'),
        get_post_type_archive_link('imagine_partenaire') ?: home_url('/') => __('Partenaires', 'imagine'),
        wp_login_url() => __('Accès au compte', 'imagine'),
        home_url('/#imagine-abonnement') => __('S’abonner', 'imagine'),
    ];
    echo '<ul>';
    foreach ($links as $url => $label) {
        echo '<li><a href="' . esc_url($url) . '">' . esc_html($label) . '</a></li>';
    }
    echo '</ul>';
}
