<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Kiosque — tous les numéros', 'imagine'); ?></h1>
<?php
imagine_list($GLOBALS['wp_query'], 2, true);
get_footer();
