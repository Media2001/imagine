<?php

declare(strict_types=1);

use Imagine\Site\PacksThematiques as P;
use Imagine\Site\AchatsNumeros as A;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) { throw new RuntimeException('C28 correction: ' . $name); }
};
$product = new WC_Product_Simple();
$product->set_name('C28 CORRECTION FICTIF transactionnel');
$product->set_status('publish');
$product->set_regular_price('3.28');
$product->set_price('3.28');
$product->set_virtual(true);
$product->set_tax_status('none');
$product->update_meta_data(P::PRODUIT, [11, 18, 25]);
$product->save();
$id = $product->get_id();
$check('direct_valide_accepte', apply_filters('woocommerce_add_to_cart_validation', true, $id, 1));
$originalCart = WC()->cart;
WC()->cart = new WC_Cart();
try {
    $key = WC()->cart->add_to_cart($id, 1);
    $check('panier_reel_constitue_avant_depublication', is_string($key) && count(WC()->cart->get_cart()) === 1);
    wp_update_post(['ID' => 18, 'post_status' => 'draft']);
    $check('pack_entier_indisponible', P::numeros(wc_get_product($id)) === []);
    $check('direct_natif_refuse', !apply_filters('woocommerce_add_to_cart_validation', true, $id, 1));
    $check('produit_natif_non_achetable', !wc_get_product($id)->is_purchasable());
    wc_clear_notices();
    do_action('woocommerce_check_cart_items');
    $check('panier_ancien_validation_refusee', wc_notice_count('error') > 0);
} finally {
    WC()->cart = $originalCart;
    wc_clear_notices();
    wp_update_post(['ID' => 18, 'post_status' => 'publish']);
}
$buyer = (int) get_option('imagine_c09_fixture')['users']['V-INSCRIT'];
$order = wc_create_order(['customer_id' => $buyer, 'status' => 'pending', 'created_via' => 'admin']);
$order->set_payment_method('');
$order->set_transaction_id('');
$lineId = $order->add_product(wc_get_product($id), 1);
$order->calculate_totals(false);
$order->save();
$orderId = $order->get_id();
$failed = false;
$fault = static function ($item) use ($lineId, &$failed): void {
    if ($item instanceof WC_Order_Item_Product && $item->get_id() === $lineId && $item->meta_exists(P::LIGNE)) {
        $failed = true;
        throw new RuntimeException('C28 APRES paiement persiste AVANT ligne');
    }
};
add_action('woocommerce_before_order_item_object_save', $fault, 99);
try {
    $order->set_date_paid(time());
    $order->set_status('processing');
    $order->save();
} catch (RuntimeException $e) {
    $failed = $e->getMessage() === 'C28 APRES paiement persiste AVANT ligne';
} finally {
    remove_action('woocommerce_before_order_item_object_save', $fault, 99);
}
$order = new WC_Order($orderId);
$check('panne_vraiment_apres_paiement_persiste_objet_recharge', $failed && $order->is_paid() && $order->get_date_paid() !== null);
$check('panne_ligne_non_persistee', !$order->get_item($lineId)->meta_exists(P::LIGNE));
$product->update_meta_data(P::PRODUIT, [18, 25, 32]);
$product->save();
$check('edition_pack_relue', P::numeros(wc_get_product($id)) === [18, 25, 32]);
$order->save();
$order = new WC_Order($orderId);
$item = $order->get_item($lineId);
$check('sauvegarde_tardive_pas_reconstruction', !$item->meta_exists(P::LIGNE));
$check('anomalie_persistante_visible_ligne', $item->meta_exists(P::ANOMALIE) && $item->get_meta(P::ANOMALIE) !== '');
$check('manque_ferme_expansion', P::instantanes([0], $item) === []);
$check('manque_ferme_droit_C14', A::droits($buyer) === []);
$check('aucune_passerelle_transaction', $order->get_payment_method() === '' && $order->get_transaction_id() === '');
// An existing but untrustworthy envelope is not reconstructed either.
$item->delete_meta_data(P::ANOMALIE);
$item->update_meta_data(P::LIGNE, ['numeros' => [32], 'paye_le' => 1, 'produit' => $id]);
$item->save();
$order = new WC_Order($orderId);
$check('date_non_fiable_fermee_avant_sauvegarde', P::instantanes([0], $order->get_item($lineId)) === []);
$order->save();
$order = new WC_Order($orderId);
$check('non_fiable_signale_pas_repare', $order->get_item($lineId)->meta_exists(P::ANOMALIE) && $order->get_item($lineId)->get_meta(P::LIGNE)['paye_le'] === 1);
$beforePost = $_POST;
$beforeUser = get_current_user_id();
try {
    wp_set_current_user(1);
    $_POST = [A::PRODUIT => '11'];
    A::enregistrer($product);
    $product->save();
    $read = wc_get_product($id);
    $check('C14_partiel_delie_pack', $read->get_meta(A::PRODUIT) === '11' && !$read->meta_exists(P::PRODUIT));
    $_POST = ['imagine_pack_present' => '1', P::PRODUIT => ['11', '18', '25']];
    P::enregistrer($product);
    $product->save();
    $read = wc_get_product($id);
    $check('pack_delie_C14_symetrique', !$read->meta_exists(A::PRODUIT) && P::numeros($read) === [11, 18, 25]);
} finally {
    $_POST = $beforePost;
    wp_set_current_user($beforeUser);
}
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => count(array_filter($checks, static fn ($v) => !$v))]);
