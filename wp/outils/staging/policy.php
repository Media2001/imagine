<?php

declare(strict_types=1);

// Liste négative A-01. Correspondances de chemins exactes : tout autre plugin garde son état.
// Un plugin absent de cette liste n'est pas déclaré sûr : réseau système toujours confiné.
return [
    'remote-control' => [
        'worker/init.php',
    ],
    'production-security' => [
        'wordfence/wordfence.php',
    ],
    // Also remove Stripe's inbound webhook handlers, not just checkout access.
    // Its stored settings are still scrubbed and switched to test mode.
    'payment-webhooks' => [
        'woocommerce-gateway-stripe/woocommerce-gateway-stripe.php',
    ],
    'mail' => [
        'wp-mail-smtp/wp_mail_smtp.php', 'wp-mail-smtp-pro/wp_mail_smtp.php',
        'post-smtp/postman-smtp.php', 'easy-wp-smtp/easy-wp-smtp.php',
        'fluent-smtp/fluent-smtp.php', 'wp-smtp/wp-smtp.php',
    ],
    'emailing' => [
        'mailin/sendinblue.php', 'brevo/brevo.php', 'mailchimp-for-wp/mailchimp-for-wp.php',
        'mailpoet/mailpoet.php', 'newsletter/plugin.php', 'fluent-crm/fluent-crm.php',
    ],
    'backup' => [
        'all-in-one-wp-migration/all-in-one-wp-migration.php', 'updraftplus/updraftplus.php',
        'duplicator/duplicator.php', 'backwpup/backwpup.php', 'wpvivid-backuprestore/wpvivid-backuprestore.php',
        'wp-staging/wp-staging.php',
    ],
    'analytics' => [
        'google-site-kit/google-site-kit.php', 'google-analytics-for-wordpress/googleanalytics.php',
        'google-analytics-dashboard-for-wp/gadwp.php', 'wp-statistics/wp-statistics.php',
        'matomo/matomo.php', 'facebook-for-woocommerce/facebook-for-woocommerce.php',
        'facebook-pixel/facebook-for-wordpress.php', 'pixelyoursite/pixelyoursite.php',
    ],
    'page-cache' => [
        'wp-rocket/wp-rocket.php', 'wp-super-cache/wp-cache.php', 'w3-total-cache/w3-total-cache.php',
        'litespeed-cache/litespeed-cache.php', 'wp-fastest-cache/wpFastestCache.php',
        'cache-enabler/cache-enabler.php',
    ],
];
