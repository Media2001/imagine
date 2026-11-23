<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Contenus', 'imagine'); ?></h1>
<?php while (have_posts()) : the_post(); ?>
    <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
<?php endwhile; ?>
<?php the_posts_pagination(); ?>
<?php get_footer(); ?>
