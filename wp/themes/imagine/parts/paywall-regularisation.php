<?php

declare(strict_types=1);
namespace Imagine\Theme;
?>
<aside class="imagine-paywall-bloc" data-imagine-bloc="regularisation" aria-label="<?php esc_attr_e('Régularisation', 'imagine'); ?>">
    <p><?php esc_html_e('Votre abonnement demande une régularisation. Pendant votre délai de grâce, la lecture reste disponible.', 'imagine'); ?></p>
    <p><a href="<?php echo esc_url(wc_get_page_permalink('myaccount') ?: wp_login_url()); ?>"><?php esc_html_e('Consulter mon compte', 'imagine'); ?></a></p>
</aside>
