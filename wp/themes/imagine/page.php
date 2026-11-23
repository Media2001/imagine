<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
while (have_posts()) : the_post();
?>
<article>
    <h1><?php the_title(); ?></h1>
    <?php the_content(); ?>
</article>
<?php endwhile; ?>
<?php get_footer(); ?>
