<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Imagine — démonstration fictive', 'imagine'); ?></h1>
<p><?php esc_html_e('Aucune donnée réelle, aucun paiement ni email sortant.', 'imagine'); ?></p>
<?php
// B14 : le composant de structure possède seul l'ordre des sections.
do_action('imagine_accueil');
?>
<?php get_search_form(); ?>
<?php get_footer(); ?>
