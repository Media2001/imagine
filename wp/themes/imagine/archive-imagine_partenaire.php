<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Nos partenaires', 'imagine'); ?></h1>
<p><?php esc_html_e('Les fiches ci-dessous sont des liens internes ; les liens sortants de leurs contenus sont déclarés commerciaux.', 'imagine'); ?></p>
<?php
imagine_partner_list($GLOBALS['wp_query']);
the_posts_pagination();
get_footer();
