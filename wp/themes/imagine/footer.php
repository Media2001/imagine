<?php

declare(strict_types=1);

namespace Imagine\Theme;
?>
    </main>
    <footer>
        <p class="imagine-notice"><?php esc_html_e('squelette, sans habillage — démonstration entièrement fictive', 'imagine'); ?></p>
        <nav aria-label="<?php esc_attr_e('Navigation de pied de page', 'imagine'); ?>">
            <?php
            if (has_nav_menu('imagine-footer')) {
                wp_nav_menu(['theme_location' => 'imagine-footer', 'container' => false, 'fallback_cb' => false]);
            }
            ?>
        </nav>
    </footer>
</div>
<?php wp_footer(); ?>
</body>
</html>
