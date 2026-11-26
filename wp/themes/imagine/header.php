<?php

declare(strict_types=1);

namespace Imagine\Theme;
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div class="imagine-shell">
    <a href="#imagine-main"><?php esc_html_e('Aller au contenu', 'imagine'); ?></a>
    <header>
        <p><a href="<?php echo esc_url(home_url('/')); ?>"><?php bloginfo('name'); ?></a></p>
        <nav aria-label="<?php esc_attr_e('Navigation principale', 'imagine'); ?>">
            <?php
            if (has_nav_menu('imagine-principal')) {
                wp_nav_menu(['theme_location' => 'imagine-principal', 'container' => false, 'fallback_cb' => false]);
            } else {
                imagine_navigation();
            }
            ?>
        </nav>
    </header>
    <main id="imagine-main" tabindex="-1">
