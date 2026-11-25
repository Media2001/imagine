<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php single_term_title(); ?></h1>
<?php
imagine_catalogue_articles($GLOBALS['wp_query']->posts);
the_posts_pagination(['prev_text' => __('Articles précédents', 'imagine'),
    'next_text' => __('Articles suivants', 'imagine')]);
get_footer();
