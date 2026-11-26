<?php

declare(strict_types=1);

namespace Imagine\Theme;

/** Structural hooks only: the designer owns the visual distinction. */
function imagine_partner_label(): void
{
    echo '<p class="imagine-partnership-label">' . esc_html__('Partenariat', 'imagine') . '</p>';
}

function imagine_partner_month(): void
{
    $partner = class_exists('Imagine\\Site\\Partenaires') ? \Imagine\Site\Partenaires::selection() : null;
    if (!$partner) {
        return;
    }
    echo '<section class="imagine-partnership" data-imagine-partenaire-mois="' . esc_attr((string) $partner->ID)
        . '" aria-labelledby="imagine-partenaire-mois">';
    imagine_partner_label();
    echo '<h2 id="imagine-partenaire-mois">' . esc_html__('Partenaire du mois', 'imagine') . '</h2><h3><a href="'
        . esc_url(get_permalink($partner)) . '">' . esc_html(get_the_title($partner)) . '</a></h3><p>'
        . esc_html(get_the_excerpt($partner)) . '</p></section>';
}

function imagine_partner_list(\WP_Query $query): void
{
    if (!$query->have_posts()) {
        echo '<p>' . esc_html__('Aucun partenaire pour le moment.', 'imagine') . '</p>';
        return;
    }
    echo '<ul class="imagine-partner-list">';
    while ($query->have_posts()) {
        $query->the_post();
        echo '<li class="imagine-partnership" data-imagine-id="' . esc_attr((string) get_the_ID()) . '">';
        imagine_partner_label();
        echo '<h2><a href="' . esc_url(get_permalink()) . '">' . esc_html(get_the_title()) . '</a></h2><p>'
            . esc_html(get_the_excerpt()) . '</p></li>';
    }
    echo '</ul>';
    wp_reset_postdata();
}
