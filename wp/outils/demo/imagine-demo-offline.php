<?php
/**
 * Plugin Name: Imagine — garde hors ligne de la démonstration
 * Description: Site fictif seulement : courriels, réseau WordPress et paiements fermés.
 */

declare(strict_types=1);

namespace Imagine\Demo;

if (!defined('ABSPATH')) {
    exit;
}

add_filter('pre_wp_mail', static fn () => false, PHP_INT_MAX);
add_filter('pre_http_request', static function () {
    return new \WP_Error('imagine_demo_offline', __('Démonstration hors ligne : connexion extérieure interdite.', 'imagine-site'));
}, PHP_INT_MAX);
add_filter('woocommerce_available_payment_gateways', static fn () => [], PHP_INT_MAX);
add_filter('pre_option_woocommerce_allow_tracking', static fn () => 'no', PHP_INT_MAX);
add_filter('pre_option_woocommerce_tracker_last_send', static fn () => PHP_INT_MAX, PHP_INT_MAX);
add_filter('automatic_updater_disabled', '__return_true', PHP_INT_MAX);
add_filter('woocommerce_helper_suppress_admin_notices', '__return_true');
add_filter('woocommerce_admin_disabled', '__return_true');
add_filter('woocommerce_allow_marketplace_suggestions', '__return_false');
add_filter('woocommerce_admin_features', static fn () => []);
add_filter('wp_resource_hints', static fn ($urls, $type) => in_array($type, ['dns-prefetch', 'preconnect'], true) ? [] : $urls, 10, 2);
