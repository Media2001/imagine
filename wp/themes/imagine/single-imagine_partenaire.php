<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
while (have_posts()) : the_post();
?>
<article class="imagine-partnership">
    <?php imagine_partner_label(); ?>
    <h1><?php the_title(); ?></h1>
    <?php the_content(); ?>
    <p><a href="<?php echo esc_url(get_post_type_archive_link('imagine_partenaire')); ?>"><?php esc_html_e('Tous les partenaires', 'imagine'); ?></a></p>
</article>
<?php endwhile; ?>
<?php get_footer(); ?>
