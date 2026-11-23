<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Agenda', 'imagine'); ?></h1>
<?php
imagine_list($GLOBALS['wp_query']);
the_posts_pagination();
get_footer();
