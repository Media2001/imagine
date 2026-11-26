<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Nos partenaires', 'imagine'); ?></h1>
<p><?php esc_html_e('Les liens vers les partenaires sont déclarés comme liens sponsorisés.', 'imagine'); ?></p>
<?php
imagine_partner_list($GLOBALS['wp_query']);
the_posts_pagination();
get_footer();
