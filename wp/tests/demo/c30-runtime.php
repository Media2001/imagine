<?php

declare(strict_types=1);

use Imagine\Site\CodesSuivis;
use Imagine\Site\CodesSuivisRegles;
use Imagine\Site\CodesSuivisConfidentialite;

if (!class_exists(CodesSuivis::class)) { throw new RuntimeException('C30 absent'); }
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) { throw new RuntimeException($name); }
};
update_option(CodesSuivis::OPTION, ['fictif-affiche' => 'FICTIF Affiche \\ Test', 'fictif-magazine' => 'FICTIF Magazine', 'fictif-evenement' => 'FICTIF Événement'], false);
$check('reglage_relu', count(CodesSuivis::configuration()) === 3);
$check('inconnu_non_range', CodesSuivisRegles::retenir('NON_LISTE_INTERDIT', CodesSuivis::configuration()) === null);
$check('mutation_inconnu_detectee', CodesSuivisRegles::retenir('NON_LISTE_INTERDIT', CodesSuivis::configuration()) !== ['code' => 'NON_LISTE_INTERDIT', 'libelle' => 'invente']);
WC()->session = new WC_Session_Handler();
WC()->session->__unset(CodesSuivis::SESSION);
CodesSuivis::retenir('fictif-affiche');
$check('session_code_valide', WC()->session->get(CodesSuivis::SESSION)['code'] === 'fictif-affiche');
CodesSuivis::retenir('fictif-magazine');
$check('dernier_valide_gagne', WC()->session->get(CodesSuivis::SESSION)['code'] === 'fictif-magazine');
CodesSuivis::retenir('NON_LISTE_INTERDIT');
$check('inconnu_ne_remplace_pas', WC()->session->get(CodesSuivis::SESSION)['code'] === 'fictif-magazine');
$user = (int)get_option('imagine_c09_fixture')['users']['P-NUMERO'];
$make = static function (string $via = 'checkout') use ($user) {
    $o = wc_create_order(['status' => 'pending', 'customer_id' => $user, 'created_via' => $via]);
    $o->set_billing_email(get_userdata($user)->user_email);
    $o->set_total('12.34');
    do_action('woocommerce_checkout_create_order', $o, []);
    $o->save();
    return $o;
};
$codeOrder = $make();
$check('impayee_pas_conversion', $codeOrder->get_meta(CodesSuivis::META) === '');
$codeOrder->set_status('completed');$codeOrder->set_date_paid(time());$codeOrder->save();
CodesSuivis::payer($codeOrder->get_id());
$paid = wc_get_order($codeOrder->get_id());
$check('payee_code_relu', $paid->get_meta(CodesSuivis::META)['code'] === 'fictif-magazine');
$check('candidat_retire', $paid->get_meta(CodesSuivis::CANDIDAT) === '');
CodesSuivis::retenir('fictif-affiche');CodesSuivis::payer($paid->get_id());
$check('paye_immuable', wc_get_order($paid->get_id())->get_meta(CodesSuivis::META)['code'] === 'fictif-magazine');
WC()->session->__unset(CodesSuivis::SESSION);CodesSuivis::retenir('NON_LISTE_INTERDIT');
$unknown = $make();
$check('commande_inconnue_aucune_meta', $unknown->get_meta(CodesSuivis::CANDIDAT) === '' && $unknown->get_meta(CodesSuivis::META) === '');
$without = $make();
// Deux vrais paniers du même produit passent par les calculs et la fabrique Woo.
$priceProduct=new WC_Product_Simple();$priceProduct->set_name('FICTIF C30 calcul des prix');$priceProduct->set_status('publish');$priceProduct->set_catalog_visibility('hidden');$priceProduct->set_virtual(true);$priceProduct->set_regular_price('12.34');$priceProduct->set_price('12.34');$priceProduct->save();
$productIds=[$priceProduct->get_id()];
$check('produit_prix_natif_present',count($productIds)===1 && (float)wc_get_product($productIds[0])->get_price()>0);
$purchase = static function (bool $withCode) use ($productIds, $user): array {
    WC()->session->__unset(CodesSuivis::SESSION);
    if($withCode){CodesSuivis::retenir('fictif-affiche');}
    WC()->customer=new WC_Customer($user);
    WC()->cart=new WC_Cart();
    if(!WC()->cart->add_to_cart((int)$productIds[0],2)){throw new RuntimeException('Panier natif refusé');}
    WC()->cart->calculate_totals();
    $id=WC()->checkout()->create_order(['billing_email'=>get_userdata($user)->user_email,'billing_country'=>'BE','shipping_country'=>'BE','payment_method'=>'']);
    if(is_wp_error($id)){throw new RuntimeException('Commande native refusée');}
    $order=wc_get_order($id);
    return ['total'=>$order->get_total(),'discount'=>$order->get_discount_total(),'tax'=>$order->get_total_tax(),'coupons'=>$order->get_coupon_codes(),'cart_total'=>WC()->cart->get_total('edit')];
};
$withoutPrice=$purchase(false);$withPrice=$purchase(true);
$samePrice=static fn(array $left,array $right):bool=>$left===$right && $left['coupons']===[];
$check('prix_identique_calcul_woo',$samePrice($withoutPrice,$withPrice));
$priceMutant=static function($cart):void{
    if(WC()->session->get(CodesSuivis::SESSION)){
        foreach($cart->get_cart() as $item){$item['data']->set_price((float)$item['data']->get_price()-1);}
    }
};
add_action('woocommerce_before_calculate_totals',$priceMutant,100);
try{$mutantPrice=$purchase(true);}finally{remove_action('woocommerce_before_calculate_totals',$priceMutant,100);}
$check('mutation_remise_code_detectee',!$samePrice($withoutPrice,$mutantPrice));
CodesSuivis::retenir('fictif-affiche');$admin = $make('imagine-c16');
$check('c16_aucun_code', $admin->get_meta(CodesSuivis::CANDIDAT) === '' && $admin->get_meta(CodesSuivis::META) === '');
$count = CodesSuivis::compter(gmdate('Y-m-d'), gmdate('Y-m-d'));
$check('compte_juste', !is_wp_error($count) && ($count['fictif-magazine'] ?? 0) === 1);
$slashOrder = $make();
$slashOrder->set_status('completed');$slashOrder->set_date_paid(time());$slashOrder->save();
CodesSuivis::payer($slashOrder->get_id());
$guest=$make();$guest->set_customer_id(0);$guest->save();
$third=$make();$third->set_customer_id(0);$third->set_billing_email('tiers-c30-fictif@example.org');$third->save();
$thirdMeta=$third->get_meta(CodesSuivis::CANDIDAT);
$store=$make('store-api');do_action('woocommerce_store_api_checkout_order_processed',$store);
$check('store_api_candidat_natif',wc_get_order($store->get_id())->get_meta(CodesSuivis::CANDIDAT)['code']==='fictif-affiche');
$store->set_status('completed');$store->set_date_paid(time());$store->save();CodesSuivis::payer($store->get_id());
$check('store_api_scelle_natif',wc_get_order($store->get_id())->get_meta(CodesSuivis::META)['code']==='fictif-affiche');
$storeSource=file_get_contents((new ReflectionClass(Automattic\WooCommerce\StoreApi\Routes\V1\Checkout::class))->getFileName());
$check('hook_store_api_present_dans_source',str_contains($storeSource,"woocommerce_store_api_checkout_order_processed"));
$export = CodesSuivisConfidentialite::exporter(get_userdata($user)->user_email);
$exportIds=array_column($export['data'],'item_id');
$check('export_invite_et_compte',in_array('imagine-c30-'.$guest->get_id().CodesSuivis::CANDIDAT,$exportIds,true) && in_array('imagine-c30-'.$paid->get_id().CodesSuivis::META,$exportIds,true));
$check('export_tiers_absent',!in_array('imagine-c30-'.$third->get_id().CodesSuivis::CANDIDAT,$exportIds,true));
$check('export_code', !is_wp_error($export) && str_contains(wp_json_encode($export), 'fictif-magazine'));
$erase = CodesSuivisConfidentialite::effacer(get_userdata($user)->user_email);
$check('effacement_relu', $erase['done'] && $erase['items_removed'] && !$erase['items_retained'] && wc_get_order($paid->get_id())->get_meta(CodesSuivis::META) === '');
$check('effacement_invite_relu',wc_get_order($guest->get_id())->get_meta(CodesSuivis::CANDIDAT)==='');
$check('effacement_tiers_preserve',wc_get_order($third->get_id())->get_meta(CodesSuivis::CANDIDAT)===$thirdMeta);
CodesSuivis::payer($paid->get_id());
$check('effacement_non_recree', wc_get_order($paid->get_id())->get_meta(CodesSuivis::META) === '');
$check('source_c27_inchangee', get_user_meta($user, Imagine\Site\Acquisition::SOURCE, true) === '');
$check('dates_invalides_refusees', is_wp_error(CodesSuivis::compter('2026-02-30', '2026-03-01')));
$check('reglage_antislash', Imagine\Site\CodesSuivisAdmin::nettoyer("fictif-test|FICTIF \\ Test") === ['fictif-test' => 'FICTIF \\ Test']);
$exportValues = [];
foreach ($export['data'] as $row) { foreach ($row['data'] as $field) { $exportValues[] = $field['value']; } }
$check('export_antislash', in_array('FICTIF Affiche \\ Test', $exportValues, true));
global $wpdb;
$journalBefore = (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name LIKE 'imagine_reglages_journal_%'");
update_option(CodesSuivis::OPTION, ['fictif-journal' => 'FICTIF Journal'], false);
$check('journal_ecrit', (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name LIKE 'imagine_reglages_journal_%'") === $journalBefore + 1);
$blockJournal = static function (string $sql): string {
    return str_starts_with($sql, 'INSERT') && str_contains($sql, 'imagine_reglages_journal_') ? 'SELECT 1' : $sql;
};
add_filter('query', $blockJournal);
try { update_option(CodesSuivis::OPTION, ['fictif-refus' => 'FICTIF Refus'], false); }
finally { remove_filter('query', $blockJournal); }
$check('journal_echec_restaure_liste', CodesSuivis::configuration() === ['fictif-journal' => 'FICTIF Journal']);
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
