<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php printf(esc_html__('Recherche : %s', 'imagine'), esc_html(get_search_query(false))); ?></h1>
<?php get_search_form(); ?>
<?php imagine_list($GLOBALS['wp_query']); ?>
<?php the_posts_pagination(); ?>
<?php get_footer(); ?>
