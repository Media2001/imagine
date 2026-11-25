<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Kiosque — tous les numéros', 'imagine'); ?></h1>
<?php
$query = $GLOBALS['wp_query'];
if ($query->have_posts()) {
    echo '<ul class="imagine-list">';
    while ($query->have_posts()) {
        $query->the_post();
        $issue = get_post();
        $status = imagine_access_status(class_exists('Imagine\\Site\\Paywall')
            ? \Imagine\Site\Paywall::decisionPdf($issue) : []);
        echo '<li data-imagine-id="' . esc_attr((string) $issue->ID) . '"><h2><a href="'
            . esc_url(get_permalink()) . '">' . esc_html(get_the_title()) . '</a></h2>';
        echo '<div class="imagine-cover">' . get_the_post_thumbnail($issue->ID, 'medium') . '</div>';
        imagine_date('imagine_sortie');
        echo '<p>' . esc_html($issue->post_excerpt) . '</p>';
        echo '<p data-imagine-access="' . esc_attr($status['code']) . '">' . esc_html($status['label']) . '</p></li>';
    }
    echo '</ul>';
} else {
    echo '<p>' . esc_html__('Aucun numéro pour le moment.', 'imagine') . '</p>';
}
the_posts_pagination(['prev_text' => __('Numéros précédents', 'imagine'),
    'next_text' => __('Numéros suivants', 'imagine')]);
get_footer();
