<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Page introuvable', 'imagine'); ?></h1>
<p><?php esc_html_e('Cette adresse ne correspond à aucun contenu.', 'imagine'); ?></p>
<p><a href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Retour à l’accueil', 'imagine'); ?></a></p>
<?php get_search_form(); ?>
<?php get_footer(); ?>
