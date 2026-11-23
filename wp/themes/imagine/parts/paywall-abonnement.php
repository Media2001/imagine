<?php

declare(strict_types=1);
namespace Imagine\Theme;
?>
<aside class="imagine-paywall-bloc" data-imagine-bloc="abonnement" aria-label="<?php esc_attr_e('Abonnement', 'imagine'); ?>">
    <p><?php esc_html_e('Votre accès actuel ne permet pas de lire la suite de cet article.', 'imagine'); ?></p>
    <p><a href="<?php echo esc_url(home_url('/#imagine-abonnement')); ?>"><?php esc_html_e('Découvrir les abonnements', 'imagine'); ?></a></p>
</aside>
