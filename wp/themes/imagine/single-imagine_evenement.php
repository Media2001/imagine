<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
while (have_posts()) : the_post();
?>
<article>
    <h1><?php the_title(); ?></h1>
    <?php imagine_date('imagine_date'); ?>
    <?php the_content(); ?>
    <p><a href="<?php echo esc_url(get_post_type_archive_link('imagine_evenement')); ?>"><?php esc_html_e('Retour à l’agenda', 'imagine'); ?></a></p>
</article>
<?php endwhile; ?>
<?php get_footer(); ?>
