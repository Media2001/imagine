<?php

declare(strict_types=1);

// Observateur de recette fictive, retiré après la recette. Le coupe-circuit B00 reste actif.
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http', 'woocommerce_order_status_changed' => 'statut',
    'woocommerce_subscription_status_updated' => 'abonnement', 'woocommerce_order_refunded' => 'remboursement'] as $hook => $kind) {
    $fn = static function ($value = null) use ($kind) {
        $counts = get_option('imagine_c25_observations', []);
        $counts[$kind] = ($counts[$kind] ?? 0) + 1;
        update_option('imagine_c25_observations', $counts, false);
        return $value;
    };
    add_filter($hook, $fn, -1000, 1);
}
