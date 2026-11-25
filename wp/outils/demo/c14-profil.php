<?php
/** V-NUM du brief = P-NUMERO de C09 : conserver le compte et la commande existants. */
declare(strict_types=1);
namespace Imagine\Demo\C14;

function guard(): void
{
    if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
        || get_option('imagine_demo_site') !== 'imagine-test-demo'
        || home_url() !== 'http://192.168.129.32:8085'
        || apply_filters('pre_wp_mail', null, []) !== false
        || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
        || WC()->payment_gateways()->get_available_payment_gateways() !== []) {
        throw new \RuntimeException('C14 refuse cette cible ou une garde hors ligne absente.');
    }
}

function profil(int $user, \WC_Order $order): array
{
    guard();
    if (get_user_meta($user, '_imagine_c09_fixture', true) !== 'P-NUMERO'
        || (int) $order->get_customer_id() !== $user
        || $order->get_meta('_imagine_c09_fixture') !== 'P-NUMERO'
        || $order->get_refunds() !== []) {
        throw new \RuntimeException('C14 refuse un profil/une commande non possédés ou remboursés.');
    }
    $issue = (int) get_option('imagine_demo_manifest')['demo-2026-t1'];
    $existing = get_page_by_path('c14-numero-fictif', OBJECT, 'product');
    if ($existing && get_post_meta($existing->ID, '_imagine_c14_fixture', true) !== 'profil') {
        throw new \RuntimeException('Collision produit C14.');
    }
    $product = new \WC_Product_Simple($existing->ID ?? 0);
    $product->set_name('C14 FICTIF — numéro à l’unité, aucun paiement réel');
    $product->set_slug('c14-numero-fictif');
    $product->set_status('private');
    $product->set_catalog_visibility('hidden');
    $product->set_virtual(true);
    $product->set_downloadable(false);
    $product->set_tax_status('none');
    $product->set_regular_price('0');
    $product->set_price('0');
    $product->update_meta_data('_imagine_c14_fixture', 'profil');
    $product->update_meta_data(\Imagine\Site\AchatsNumeros::PRODUIT, $issue);
    $product->save();
    $items = $order->get_items();
    $first = count($items) === 1 ? reset($items) : null;
    if (!$first || $first->get_product_id() !== $product->get_id()
        || (int) $first->get_meta(\Imagine\Site\AchatsNumeros::LIGNE) !== $issue) {
        $order->remove_order_items();
        $order->add_product($product, 1, ['subtotal' => '0', 'total' => '0']);
    }
    $order->set_payment_method('');
    $order->set_payment_method_title('FICTIF C14 — état payé administratif, aucun règlement');
    $order->set_transaction_id('');
    $order->set_status('processing');
    // Fixture déclarée, jamais payment_complete() ni appel d'une passerelle.
    if (!$order->get_date_paid()) {
        $order->set_date_paid(time() - DAY_IN_SECONDS);
    }
    $order->set_customer_note('FICTIF C14 : état payé et date de fixture, zéro transaction réelle.');
    $order->calculate_totals(false);
    $order->save();
    $read = wc_get_order($order->get_id());
    $result = ['user' => $user, 'order' => $read->get_id(), 'product' => $product->get_id(),
        'issue' => $issue, 'status' => $read->get_status(), 'date_paid' => (bool) $read->get_date_paid(),
        'no_gateway_transaction' => $read->get_payment_method() === '' && $read->get_transaction_id() === '',
        'mapped_issue' => \Imagine\Site\AchatsNumeros::numero(wc_get_product($product->get_id()))];
    if ($result['status'] !== 'processing' || !$result['date_paid'] || !$result['no_gateway_transaction']
        || $result['mapped_issue'] !== $issue) {
        throw new \RuntimeException('Profil C14 non relu.');
    }
    return $result;
}
