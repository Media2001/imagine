<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
while (have_posts()) : the_post();
    // Une seule décision/sortie C08 ; aucune lecture supplémentaire du corps stocké.
    ob_start();
    imagine_article_body();
    $articleBody = (string) ob_get_clean();
    $readingMinutes = imagine_reading_minutes($articleBody);
?>
<div id="imagine-reading-tools" hidden>
    <button type="button" id="imagine-reading-toggle" aria-pressed="false" aria-controls="imagine-reading-options"
        data-enter-label="<?php esc_attr_e('Lire l’article', 'imagine'); ?>"
        data-exit-label="<?php esc_attr_e('Quitter le mode lecture', 'imagine'); ?>"><?php esc_html_e('Lire l’article', 'imagine'); ?></button>
    <div id="imagine-reading-options" hidden></div>
</div>
<article class="imagine-article" data-imagine-reading-id="<?php echo esc_attr((string) get_the_ID()); ?>">
    <header>
        <h1><?php the_title(); ?></h1>
        <p class="imagine-chapo"><?php echo esc_html(get_post_field('post_excerpt', get_the_ID())); ?></p>
        <p><?php esc_html_e('Par', 'imagine'); ?> <?php echo esc_html(get_the_author()); ?></p>
        <?php $issue = (int) get_post_meta(get_the_ID(), 'imagine_numero_id', true); ?>
        <?php if ($issue && get_post_status($issue) === 'publish') : ?>
            <p><?php esc_html_e('Numéro d’appartenance :', 'imagine'); ?> <a href="<?php echo esc_url(get_permalink($issue)); ?>"><?php echo esc_html(get_the_title($issue)); ?></a></p>
        <?php endif; ?>
        <?php $terms = get_the_term_list(get_the_ID(), 'imagine_thematique', '', ', '); ?>
        <?php if ($terms && !is_wp_error($terms)) : ?>
            <p><?php esc_html_e('Thématiques :', 'imagine'); ?> <?php echo wp_kses_post($terms); ?></p>
        <?php endif; ?>
        <p data-imagine-reading-time><?php echo esc_html(sprintf(
            _n('Temps de lecture estimé : %d minute (texte accessible).', 'Temps de lecture estimé : %d minutes (texte accessible).', $readingMinutes, 'imagine'),
            $readingMinutes
        )); ?></p>
    </header>
    <div class="imagine-article-body" data-imagine-body="article">
        <?php echo $articleBody; // Sortie HTML autorisée et filtrée par imagine_article_body(). ?>
    </div>
</article>
<?php endwhile; ?>
<?php get_footer(); ?>
