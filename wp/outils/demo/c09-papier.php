<?php
/** Rejeu ciblé du calendrier C09 A-PAPIER, consigne du 26/11/2026 à 1 h 30. */
declare(strict_types=1);
namespace Imagine\Demo\C09;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085') {
    throw new \RuntimeException('C09 refuse cette cible.');
}
$mu = realpath(WPMU_PLUGIN_DIR . '/imagine-demo-offline.php');
if (!$mu || !in_array($mu, array_map('realpath', get_included_files()), true)
    || apply_filters('pre_wp_mail', null, []) !== false
    || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
    || apply_filters('woocommerce_available_payment_gateways', []) !== []) {
    throw new \RuntimeException('Garde hors ligne C09 absente.');
}
require_once __DIR__ . '/c09-calendar.php';
$fixture = get_option('imagine_c09_fixture');
$sub = wcs_get_subscription((int) ($fixture['subscriptions']['A-PAPIER'] ?? 0));
if (!$sub || $sub->get_meta('_imagine_c09_fixture') !== 'A-PAPIER'
    || $sub->get_meta('imagine_demo_fictif') !== '1'
    || !$sub->has_status('active') || !$sub->is_manual()
    || $sub->get_payment_method() !== '' || $sub->get_transaction_id() !== ''
    || $sub->get_payment_tokens() !== []
    || $sub->get_customer_id() !== (int) $fixture['users']['A-PAPIER']
    || $sub->get_parent_id() !== (int) $fixture['orders']['A-PAPIER']) {
    throw new \RuntimeException('Profil C09 A-PAPIER étranger ou hors état de départ.');
}
$before = $sub->get_date('next_payment');
$scheduled = as_next_scheduled_action('woocommerce_scheduled_subscription_payment', ['subscription_id' => $sub->get_id()]);
if ($scheduled !== false && $scheduled === $sub->get_time('next_payment')) {
    echo wp_json_encode(['profile' => 'A-PAPIER', 'id' => $sub->get_id(), 'replayed' => false, 'next_payment' => $before]);
    return;
}
// Même horloge et même fonction que c09-seed.php, sans réinitialiser les autres profils.
$instant = now();
$next = papierDue($instant);
$sub->update_dates(['next_payment' => $next], 'gmt');
$sub->save();
echo wp_json_encode(['profile' => 'A-PAPIER', 'id' => $sub->get_id(), 'replayed' => true,
    'calendar_at' => $instant->format('Y-m-d H:i:s'), 'before_next_payment' => $before, 'next_payment' => $next]);
