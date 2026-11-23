<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
while (have_posts()) : the_post();
?>
<article>
    <h1><?php the_title(); ?></h1>
    <div class="imagine-cover"><?php echo get_the_post_thumbnail(get_the_ID(), 'medium'); ?></div>
    <?php imagine_date('imagine_sortie'); ?>
    <p><?php echo esc_html(get_the_excerpt()); ?></p>
    <section aria-labelledby="imagine-contents">
        <h2 id="imagine-contents"><?php esc_html_e('Sommaire', 'imagine'); ?></h2>
        <?php imagine_list(new \WP_Query([
            'post_type' => 'post', 'post_status' => 'publish', 'posts_per_page' => -1,
            'meta_key' => 'imagine_numero_id', 'meta_value' => get_the_ID(),
            'orderby' => ['menu_order' => 'ASC', 'ID' => 'ASC'],
        ]), 3); ?>
    </section>
    <?php $pdf = wp_get_attachment_url((int) get_post_meta(get_the_ID(), 'imagine_pdf_id', true)); ?>
    <?php if ($pdf) : ?>
        <p><a href="<?php echo esc_url($pdf); ?>"><?php esc_html_e('Ouvrir le PDF factice du numéro', 'imagine'); ?></a></p>
    <?php endif; ?>
</article>
<?php endwhile; ?>
<?php get_footer(); ?>
