<?php

declare(strict_types=1);
namespace Imagine\Theme;
?>
<aside class="imagine-paywall-bloc" data-imagine-bloc="connexion" aria-label="<?php esc_attr_e('Accès à cet article', 'imagine'); ?>">
    <p><?php esc_html_e('Cet article est réservé. Connectez-vous avec votre compte abonné ou découvrez les abonnements.', 'imagine'); ?></p>
    <p><a href="<?php echo esc_url(wp_login_url(get_permalink())); ?>"><?php esc_html_e('Se connecter', 'imagine'); ?></a> · <a href="<?php echo esc_url(home_url('/#imagine-abonnement')); ?>"><?php esc_html_e('S’abonner', 'imagine'); ?></a></p>
</aside>
