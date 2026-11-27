<?php

declare(strict_types=1);

// Démonstration fictive seulement : ne change pas le mode Coming Soon de la boutique.
// Exception native Woo limitée à la fiche publique du produit C28 déclaré fictif.
add_filter('woocommerce_coming_soon_exclude', static function (bool $excluded): bool {
    if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
        || !is_singular('product')) {
        return $excluded;
    }
    $f = get_option('imagine_c28_fixture', []);
    return $excluded || ((int) get_queried_object_id() === (int) ($f['product'] ?? 0)
        && get_post_meta(get_queried_object_id(), '_imagine_c28_fictif', true) === '1');
});
