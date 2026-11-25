<?php

declare(strict_types=1);

namespace Imagine\Demo;

/** Démo B04 seulement : ni thème livré, ni option de visibilité Woo modifiée. */
function imagine_b04_product_preview(bool $excluded): bool
{
    if ($excluded) {
        return true;
    }
    return wp_get_environment_type() === 'local'
        && get_option('imagine_demo_site') === 'imagine-test-demo'
        && rtrim(home_url(), '/') === 'http://192.168.129.32:8085'
        && in_array($_SERVER['REQUEST_METHOD'] ?? '', ['GET', 'HEAD'], true)
        && is_singular('product')
        && get_post_meta(get_queried_object_id(), '_imagine_b04_fixture', true) === 'product-v1';
}
add_filter('woocommerce_coming_soon_exclude', __NAMESPACE__ . '\\imagine_b04_product_preview');
