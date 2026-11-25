<?php
/** Recette synthétique native C14 : vrais objets Woo, aucun transport financier. */
declare(strict_types=1);
use Imagine\Site\AchatsNumeros;
use Imagine\Site\Paywall;
require_once WP_CONTENT_DIR . '/imagine-demo-build/c14-profil.php';
\Imagine\Demo\C14\guard();
$checks = [];
$original = get_current_user_id();
$ids = ['orders' => [], 'posts' => [], 'users' => []];
$token = wp_generate_uuid4();
$owned = '_imagine_c14_fixture';
$manifest = get_option('imagine_demo_manifest');
$a = (int) $manifest['demo-2026-t1'];
$b = (int) $manifest['demo-2026-t2'];
$article = [];
try {
    $user = wp_insert_user(['user_login' => 'imagine-c14-' . $token, 'user_email' => 'c14-' . $token . '@example.org',
        'display_name' => 'Personnage Fictif C14', 'role' => 'customer', 'meta_input' => [$owned => $token]]);
    if (is_wp_error($user)) { throw new RuntimeException('Utilisateur C14 impossible.'); }
    $ids['users'][] = $user;
    wp_set_current_user($user);
    foreach (['a' => $a, 'b' => $b] as $key => $issue) {
        $id = wp_insert_post(['post_type' => 'post', 'post_status' => 'publish', 'post_title' => 'Témoin FICTIF C14 ' . $token . $key,
            'post_content' => 'Sentinelle réservée C14 entièrement fictive.', 'post_excerpt' => 'Extrait public fictif C14.',
            'meta_input' => [$owned => $token, 'imagine_reserve' => '1', 'imagine_numero_id' => $issue]], true);
        if (is_wp_error($id)) { throw new RuntimeException('Article C14 impossible.'); }
        $ids['posts'][] = $id;
        $article[$key] = get_post($id);
    }
    $product = new WC_Product_Simple();
    $product->set_name('Produit éphémère FICTIF C14 ' . $token);
    $product->set_status('private'); $product->set_catalog_visibility('hidden');
    $product->set_virtual(true); $product->set_tax_status('none');
    $product->set_regular_price('10'); $product->set_price('10');
    $product->update_meta_data($owned, $token);
    $product->update_meta_data(AchatsNumeros::PRODUIT, $a);
    $product->save(); $ids['posts'][] = $product->get_id();
    $make = static function (int $customer) use (&$ids, $owned, $token, $product): WC_Order {
        $o = wc_create_order(['customer_id' => $customer, 'status' => 'pending', 'created_via' => 'admin']);
        if (is_wp_error($o)) { throw new RuntimeException('Commande C14 impossible.'); }
        $ids['orders'][] = $o->get_id();
        $o->update_meta_data($owned, $token);
        $o->set_payment_method(''); $o->set_transaction_id('');
        $o->add_product($product, 1, ['subtotal' => '10', 'total' => '10']);
        $o->calculate_totals(false); $o->save();
        return $o;
    };
    $allowed = static fn (): bool => Paywall::decision($article['a'])['complet']
        && Paywall::decisionPdf(get_post($a))['complet'];
    $closed = static fn (): bool => !Paywall::decision($article['a'])['complet']
        && !Paywall::decisionPdf(get_post($a))['complet'];
    $order = $make($user);
    $checks['champ_mapping_natif'] = AchatsNumeros::numero(wc_get_product($product->get_id())) === $a;
    $items = $order->get_items(); $item = reset($items);
    $checks['instantane_ligne_natif'] = (int) wc_get_order_item_meta($item->get_id(), AchatsNumeros::LIGNE, true) === $a;
    foreach (['pending', 'on-hold', 'failed', 'cancelled'] as $status) {
        $order->set_status($status); $order->save();
        $checks['non_payee_' . $status . '_articles_PDF'] = $closed();
    }
    foreach (['processing', 'completed'] as $status) {
        $order->set_status($status); $order->set_date_paid(time() - DAY_IN_SECONDS); $order->save();
        $checks['payee_' . $status . '_articles_PDF'] = $allowed();
    }
    $checks['motif_moteur_numero_achete'] = Paywall::decision($article['a'])['motif'] === 'numero_achete';
    $checks['autre_numero_articles_PDF_fermes'] = !Paywall::decision($article['b'])['complet'] && !Paywall::decisionPdf(get_post($b))['complet'];
    wp_set_current_user(0);
    $checks['anonyme_apres_payee_articles_PDF_fermes'] = $closed();
    wp_set_current_user($user);
    $order->set_date_paid(time() + DAY_IN_SECONDS); $order->save();
    $checks['date_acquisition_future_fermee'] = $closed();
    $order->set_date_paid(time() - DAY_IN_SECONDS); $order->save();
    $checks['retour_date_valide'] = $allowed();
    $order->set_customer_id(0); $order->set_billing_email(get_userdata($user)->user_email); $order->save();
    $checks['invite_email_identique_aucun_droit'] = $closed();
    $order->set_customer_id($user); $order->save();
    $checks['client_natif_retabli'] = $allowed();
    // Accord positif suivi immédiatement de mutation : aucune invalidation manuelle.
    $refund = wc_create_refund(['order_id' => $order->get_id(), 'amount' => '1',
        'refund_payment' => false, 'restock_items' => false, 'reason' => 'FICTIF C14 sans transfert']);
    if (is_wp_error($refund)) { throw new RuntimeException('Remboursement synthétique C14 impossible.'); }
    $ids['orders'][] = $refund->get_id();
    $checks['remboursement_partiel_non_ventile_revoque_meme_requete'] = $closed();
    $checks['remboursement_sans_passerelle'] = !$refund->get_refunded_payment();
    $refund->delete(true);
    $checks['suppression_remboursement_relit_etat_natif'] = $allowed();
    // Woo conserve un total_refunded en cache après delete() brut : utiliser une
    // autre commande pour le témoin total, sans purger les caches du sujet.
    $order->set_status('cancelled'); $order->save();
    $order = $make($user); $order->set_status('processing');
    $order->set_date_paid(time() - DAY_IN_SECONDS); $order->save();
    $refund = wc_create_refund(['order_id' => $order->get_id(), 'amount' => '10',
        'refund_payment' => false, 'restock_items' => false]);
    if (is_wp_error($refund)) { throw new RuntimeException('Remboursement total C14 impossible : ' . $refund->get_error_code() . ' ' . $refund->get_error_message()); }
    $ids['orders'][] = $refund->get_id();
    $checks['remboursement_total_revoque'] = $closed();
    $refund->delete(true);
    $order = wc_get_order($order->get_id()); $order->set_status('processing'); $order->save();
    $checks['retablissement_paye'] = $allowed();
    $product->update_meta_data(AchatsNumeros::PRODUIT, $b); $product->save();
    $checks['reaffectation_produit_revoque_sans_ouvrir_autre'] = $closed()
        && !Paywall::decision($article['b'])['complet'] && !Paywall::decisionPdf(get_post($b))['complet'];
    $product->delete_meta_data(AchatsNumeros::PRODUIT); $product->save();
    $checks['retrait_mapping_revoque'] = $closed();
    $product->update_meta_data(AchatsNumeros::PRODUIT, $a); $product->save();
    $checks['mapping_retabli'] = $allowed();
    $items = $order->get_items(); $item = reset($items);
    $item->delete_meta_data(AchatsNumeros::LIGNE); $item->save();
    $checks['ancienne_ligne_sans_instantane_fermee_pas_de_retrooctroi'] = $closed()
        && !wc_get_order_item_meta($item->get_id(), AchatsNumeros::LIGNE, true);
    $item->update_meta_data(AchatsNumeros::LIGNE, $a); $item->save();
    $checks['instantane_retabli'] = $allowed();
    $item->set_quantity(0); $item->save();
    $checks['quantite_zero_revoque'] = $closed();
    $item->set_quantity(1); $item->save();
    $checks['quantite_retablie'] = $allowed();
    $order->remove_item($item->get_id()); $order->save();
    $checks['suppression_ligne_revoque'] = $closed();
    $order->add_product($product, 1, ['subtotal' => '10', 'total' => '10']); $order->save();
    $checks['nouvelle_ligne_retablit'] = $allowed();
    $second = $make($user); $second->set_status('processing'); $second->set_date_paid(time() - DAY_IN_SECONDS); $second->save();
    $order->set_status('cancelled'); $order->save();
    $checks['autre_achat_valide_conserve_droit'] = $allowed();
    $second->delete(true);
    $checks['suppression_dernier_achat_valide_revoque'] = $closed();
    $order = wc_get_order($order->get_id()); $order->set_status('processing');
    $order->set_date_paid(time() - DAY_IN_SECONDS); $order->save();
    $checks['ordre_paye_apres_retrait_retabli'] = $allowed();
    $deletedOrder = $order->get_id();
    $order->delete(false);
    $checks['mise_corbeille_commande_revoque'] = $closed();
    $order = wc_get_order($deletedOrder);
    if ($order) { $order->delete(true); }
    $checks['suppression_commande_definitive_revoque'] = $closed();
    $order = $make($user); $order->set_status('processing'); $order->set_date_paid(time() - DAY_IN_SECONDS); $order->save();
    $checks['nouvelle_commande_valide'] = $allowed();
    $product->delete(true);
    $checks['produit_supprime_revoque'] = $closed();
    $checks['HPOS_natif_actif'] = \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled();
    $checks['aucun_moyen_paiement_transaction'] = $order->get_payment_method() === '' && $order->get_transaction_id() === '';
} finally {
    foreach (array_reverse($ids['orders']) as $id) {
        $o = wc_get_order($id);
        if ($o && ($o->get_type() === 'shop_order_refund' || $o->get_meta($owned) === $token)) { $o->delete(true); }
    }
    foreach (array_reverse($ids['posts']) as $id) {
        if (get_post_meta($id, $owned, true) === $token) { wp_delete_post($id, true); }
    }
    require_once ABSPATH . 'wp-admin/includes/user.php';
    foreach ($ids['users'] as $id) {
        if (get_user_meta($id, $owned, true) === $token) { wp_delete_user($id); }
    }
    wp_set_current_user($original);
}
$checks['nettoyage_commandes_relu'] = !array_filter($ids['orders'], static fn ($id) => (bool) wc_get_order($id));
$checks['nettoyage_posts_relu'] = !array_filter($ids['posts'], static fn ($id) => (bool) get_post($id));
$checks['nettoyage_comptes_relu'] = !array_filter($ids['users'], static fn ($id) => (bool) get_userdata($id));
echo wp_json_encode($checks);
if (in_array(false, $checks, true)) { WP_CLI::halt(1); }
