<?php

declare(strict_types=1);

use Imagine\Site\PacksThematiques as Packs;
use Imagine\Site\AchatsNumeros;
use Imagine\Site\Paywall;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) {
        echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
        throw new RuntimeException('C28: ' . $name);
    }
};
$check('adaptateur_pack_present', class_exists(Packs::class));
$buyer = (int) get_option('imagine_c09_fixture')['users']['V-INSCRIT'];
$issues = [11, 18, 25];
$product = new WC_Product_Simple();
$product->set_name('C28 test transactionnel FICTIF');
$product->set_status('publish');
$product->set_virtual(true);
$product->set_tax_status('none');
$product->set_regular_price('3.28');
$product->set_price('3.28');
$product->update_meta_data(Packs::PRODUIT, $issues);
$product->save();
$order = wc_create_order(['customer_id' => $buyer, 'status' => 'pending', 'created_via' => 'admin']);
$order->set_payment_method('');
$order->set_transaction_id('');
$itemId = $order->add_product($product, 1);
$order->calculate_totals(false);
$order->save();
$item = $order->get_item($itemId);
$check('pas_instantane_avant_paiement', !$item->meta_exists(Packs::LIGNE));
$check('C14_pas_droit_avant_paiement', AchatsNumeros::droits($buyer) === []);
$failSave = static function ($saving) use ($order): void {
    if ($saving instanceof WC_Order && $saving->get_id() === $order->get_id()) {
        throw new RuntimeException('C28 paiement non persisté témoin');
    }
};
add_action('woocommerce_before_order_object_save', $failSave, 99);
try {
    $order->set_date_paid(time());
    $order->set_status('processing');
    $order->save();
} catch (RuntimeException $e) {
    if ($e->getMessage() !== 'C28 paiement non persisté témoin') {
        throw $e;
    }
} finally {
    remove_action('woocommerce_before_order_object_save', $failSave, 99);
}
$order = wc_get_order($order->get_id());
$check('paiement_non_persiste_pas_instantane', !$order->get_item($itemId)->meta_exists(Packs::LIGNE));
// La liste du panier n'est PAS la liste acquise : ajout effectué avant paiement.
$product->update_meta_data(Packs::PRODUIT, [11, 18, 32]);
$product->save();
$order = wc_get_order($order->get_id());
$order->payment_complete();
$order = wc_get_order($order->get_id());
$item = $order->get_item($itemId);
$snapshot = $item->get_meta(Packs::LIGNE, true, 'edit');
$check('instantane_AU_paiement_pas_au_panier', ($snapshot['numeros'] ?? null) === [11, 18, 32]);
$check('date_instantane_date_paiement', ($snapshot['paye_le'] ?? null) === $order->get_date_paid()->getTimestamp());
$rights = AchatsNumeros::droits($buyer);
$check('trois_achats_via_C14', array_column($rights, 'numero') === ['11', '18', '32']);
wp_set_current_user($buyer);
foreach ([11, 18, 32] as $id) {
    $decision = Paywall::decisionPdf(get_post($id));
    $check('C06_numero_achete_' . $id, $decision['complet'] && $decision['motif'] === 'numero_achete');
}
$product->update_meta_data(Packs::PRODUIT, [18, 25, 32]);
$product->save();
$order->save();
$check('ajout_retrait_sans_retrooctroi', array_column(AchatsNumeros::droits($buyer), 'numero') === ['11', '18', '32']);
$check('instantane_immuable_apres_resauvegarde', wc_get_order($order->get_id())->get_item($itemId)->get_meta(Packs::LIGNE, true, 'edit') === $snapshot);
wp_set_current_user(0);
$check('anonyme_pas_droit', !Paywall::decisionPdf(get_post(11))['complet']);
$check('tiers_pas_droit', AchatsNumeros::droits((int) get_option('imagine_c09_fixture')['users']['V-DEC-FIN']) === []);
wp_set_current_user($buyer);
$refund = wc_create_refund(['order_id' => $order->get_id(), 'amount' => '1', 'refund_payment' => false, 'restock_items' => false, 'reason' => 'C28 FICTIF sans transfert']);
$check('remboursement_natif_sans_passerelle', $refund instanceof WC_Order_Refund && !$refund->get_refunded_payment());
update_option(AchatsNumeros::REMBOURSEMENT, 'commande');
$check('C14_commande_partiel_ferme_pack', AchatsNumeros::droits($buyer) === []);
update_option(AchatsNumeros::REMBOURSEMENT, 'ligne');
$check('C14_ligne_non_ventile_conserve_pack', count(AchatsNumeros::droits($buyer)) === 3);
$refund2 = wc_create_refund(['order_id' => $order->get_id(), 'amount' => '1', 'line_items' => [$itemId => ['qty' => 0, 'refund_total' => 1, 'refund_tax' => []]], 'refund_payment' => false, 'restock_items' => false]);
$check('C14_ligne_pack_remboursee_ferme_tous_ses_numeros', $refund2 instanceof WC_Order_Refund && AchatsNumeros::droits($buyer) === []);
$refund3 = wc_create_refund(['order_id' => $order->get_id(), 'amount' => '1.28', 'refund_payment' => false, 'restock_items' => false]);
foreach (['commande', 'ligne'] as $policy) {
    update_option(AchatsNumeros::REMBOURSEMENT, $policy);
    $check('C14_total_ferme_' . $policy, $refund3 instanceof WC_Order_Refund && AchatsNumeros::droits($buyer) === []);
}
$make = static function () use ($buyer, $product): WC_Order {
    $o = wc_create_order(['customer_id' => $buyer, 'status' => 'pending', 'created_via' => 'admin']);
    $o->add_product(wc_get_product($product->get_id()), 1);
    $o->calculate_totals(false);
    $o->save();
    return $o;
};
$legacy = $make();
$lines = $legacy->get_items();
$line = reset($lines);
$line->delete_meta_data(Packs::CANDIDAT);
$line->save();
$legacy->payment_complete();
$check('ancienne_ligne_sans_marque_aucun_retrooctroi', AchatsNumeros::droits($buyer) === []);
$empty = $make();
$product->delete_meta_data(Packs::PRODUIT);
$product->save();
$refused = false;
try {
    $empty->set_date_paid(time());
    $empty->set_status('processing');
    $empty->save();
} catch (RuntimeException $e) {
    $refused = str_contains($e->getMessage(), 'pack indisponible');
}
$product->update_meta_data(Packs::PRODUIT, [11, 18, 25]);
$product->save();
$empty = wc_get_order($empty->get_id());
$check('pack_retire_paiement_refuse_sans_droit_vide', $refused && !$empty->is_paid() && AchatsNumeros::droits($buyer) === []);
$owner = (int) get_option('imagine_c09_fixture')['users']['P-NUMERO'];
$already = wc_create_order(['customer_id' => $owner, 'status' => 'pending', 'created_via' => 'admin']);
$already->add_product(wc_get_product($product->get_id()), 1);
$already->calculate_totals(false);
$already->save();
$check('numero_deja_possede_aucune_remise', $already->get_total() === '3.28'
    && in_array('11', array_column(AchatsNumeros::droits($owner), 'numero'), true));
$already->payment_complete();
$check('numero_deja_possede_pack_vendable', count(AchatsNumeros::droits($owner)) === 4);
$source = wc_get_product($product->get_id());
$source->delete(true);
$check('produit_supprime_acquisitions_conservees', count(AchatsNumeros::droits($owner)) === 4);
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => count(array_filter($checks, static fn ($v) => !$v))]);
