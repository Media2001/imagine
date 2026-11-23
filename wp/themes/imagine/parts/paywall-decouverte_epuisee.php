<?php

declare(strict_types=1);
namespace Imagine\Theme;
?>
<aside class="imagine-paywall-bloc" data-imagine-bloc="decouverte_epuisee" aria-label="<?php esc_attr_e('Accès découverte', 'imagine'); ?>">
    <p><?php esc_html_e('Votre accès découverte est épuisé. Vous pouvez poursuivre avec un abonnement.', 'imagine'); ?></p>
    <p><a href="<?php echo esc_url(home_url('/#imagine-abonnement')); ?>"><?php esc_html_e('Découvrir les abonnements', 'imagine'); ?></a></p>
</aside>
