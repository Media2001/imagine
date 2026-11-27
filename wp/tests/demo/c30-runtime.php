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
    CodesSuivis::candidat($o, []);
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
$check('prix_identique', $without->get_total() === $paid->get_total() && $paid->get_coupon_codes() === []);
CodesSuivis::retenir('fictif-affiche');$admin = $make('imagine-c16');
$check('c16_aucun_code', $admin->get_meta(CodesSuivis::CANDIDAT) === '' && $admin->get_meta(CodesSuivis::META) === '');
$count = CodesSuivis::compter(gmdate('Y-m-d'), gmdate('Y-m-d'));
$check('compte_juste', !is_wp_error($count) && ($count['fictif-magazine'] ?? 0) === 1);
$export = CodesSuivisConfidentialite::exporter(get_userdata($user)->user_email);
$check('export_code', !is_wp_error($export) && str_contains(wp_json_encode($export), 'fictif-magazine'));
$erase = CodesSuivisConfidentialite::effacer(get_userdata($user)->user_email);
$check('effacement_relu', $erase['done'] && $erase['items_removed'] && !$erase['items_retained'] && wc_get_order($paid->get_id())->get_meta(CodesSuivis::META) === '');
CodesSuivis::payer($paid->get_id());
$check('effacement_non_recree', wc_get_order($paid->get_id())->get_meta(CodesSuivis::META) === '');
$check('source_c27_inchangee', get_user_meta($user, Imagine\Site\Acquisition::SOURCE, true) === '');
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
