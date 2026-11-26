<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Imagine — démonstration fictive', 'imagine'); ?></h1>
<p><?php esc_html_e('Aucune donnée réelle, aucun paiement ni email sortant.', 'imagine'); ?></p>
<section aria-labelledby="imagine-latest-issue">
    <h2 id="imagine-latest-issue"><?php esc_html_e('Dernier numéro', 'imagine'); ?></h2>
    <?php imagine_list(imagine_issue_query(1), 3, true); ?>
    <p><a href="<?php echo esc_url(get_post_type_archive_link('imagine_numero')); ?>"><?php esc_html_e('Tous les numéros — kiosque', 'imagine'); ?></a></p>
</section>
<section aria-labelledby="imagine-latest-posts">
    <h2 id="imagine-latest-posts"><?php esc_html_e('Derniers articles', 'imagine'); ?></h2>
    <?php imagine_list(new \WP_Query(['post_type' => 'post', 'posts_per_page' => 5, 'post_status' => 'publish', 'orderby' => ['date' => 'DESC', 'ID' => 'DESC']]), 3); ?>
</section>
<section aria-labelledby="imagine-thematiques">
    <h2 id="imagine-thematiques"><?php esc_html_e('Thématiques', 'imagine'); ?></h2>
    <?php $terms = get_terms(['taxonomy' => 'imagine_thematique', 'hide_empty' => true]); ?>
    <?php if (!is_wp_error($terms) && $terms) : ?>
        <ul>
        <?php foreach ($terms as $term) : ?>
            <li><a href="<?php echo esc_url(get_term_link($term)); ?>"><?php echo esc_html($term->name); ?></a></li>
        <?php endforeach; ?>
        </ul>
    <?php else : ?>
        <p><?php esc_html_e('Aucune thématique pour le moment.', 'imagine'); ?></p>
    <?php endif; ?>
</section>
<section aria-labelledby="imagine-agenda">
    <h2 id="imagine-agenda"><?php esc_html_e('Agenda', 'imagine'); ?></h2>
    <p><a href="<?php echo esc_url(get_post_type_archive_link('imagine_evenement')); ?>"><?php esc_html_e('Voir les événements fictifs', 'imagine'); ?></a></p>
</section>
<section aria-labelledby="imagine-abonnement">
    <h2 id="imagine-abonnement"><?php esc_html_e('S’abonner', 'imagine'); ?></h2>
    <p><?php esc_html_e('Emplacement du futur lien d’abonnement. Le tunnel n’est pas réalisé dans B-01 ; aucun achat n’est possible.', 'imagine'); ?></p>
</section>
<?php imagine_partner_month(); ?>
<?php get_search_form(); ?>
<?php get_footer(); ?>
