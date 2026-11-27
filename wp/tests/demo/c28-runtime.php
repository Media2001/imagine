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
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => count(array_filter($checks, static fn ($v) => !$v))]);
