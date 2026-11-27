<?php

declare(strict_types=1);

use Imagine\Site\{ContactBrevo, Newsletters, Personnalisation, Cooperateurs};

if (!class_exists(ContactBrevo::class)) {
    fwrite(STDERR, "C29 adaptateur absent\n"); exit(1);
}
$fixture = get_option('imagine_c09_fixture');
$users = $fixture['users'];
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) { throw new RuntimeException($name); }
};
$expected = require __DIR__ . '/c29-attendus.php';
$check('catalogue_27_profils_exact', count($expected) === 27 && array_keys($users) === array_keys($expected));
$catalogue = [['id' => 'principale', 'titre' => 'FICTIF C29', 'presentation' => 'Essai', 'principale' => true]];
update_option(Newsletters::CATALOGUE, $catalogue, false);
update_option(Personnalisation::CATALOGUE, [['id' => 'fictif', 'titre' => 'FICTIF C29', 'multiple' => false,
    'choix' => [['id' => 'a', 'titre' => 'FICTIF A']]]], false);
$map = [];
foreach ($fixture['tariffs'] as $code => $id) { $map[(string)$id] = $code; }
update_option(ContactBrevo::TARIFS, $map, false);
$date = '2026-11-27T00:00:00Z';
foreach ($users as $code => $id) {
    $pref = str_starts_with($code, 'E-') || $code === 'V-INSCRIT' ? []
        : ['principale' => ['choix' => $code !== 'V-DEC-FIN', 'origine' => 'lecteur', 'date_utc' => $date]];
    update_user_meta($id, Newsletters::META, $pref);
    update_user_meta($id, Cooperateurs::META, ['cooperateur' => $code === 'P-COOP']);
    delete_user_meta($id, Personnalisation::META);
    delete_user_meta($id, Personnalisation::CONSENTEMENT);
}
update_user_meta($users['A-SANSMAIL'], Imagine\Site\SansEmail::META, '1');
update_user_meta($users['A-CARTE'], Personnalisation::META, ['fictif' => ['choix' => ['a'], 'date_utc' => $date]]);
update_user_meta($users['A-CARTE'], Personnalisation::CONSENTEMENT, ['accord' => true, 'date_utc' => $date]);
$writes = []; $outgoing = [];
$guard = static function (string $sql) use (&$writes): string {
    if (!preg_match('/^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $sql)) {
        $writes[] = $sql; throw new RuntimeException('C29 écriture SQL');
    }
    return $sql;
};
$http = static function () use (&$outgoing): never { $outgoing[] = 'http'; throw new RuntimeException('C29 HTTP'); };
$mail = static function () use (&$outgoing): never { $outgoing[] = 'mail'; throw new RuntimeException('C29 mail'); };
add_filter('query', $guard, PHP_INT_MAX);
add_filter('pre_http_request', $http, PHP_INT_MAX);
add_filter('pre_wp_mail', $mail, PHP_INT_MAX);
$actual = [];
try {
    foreach ($users as $code => $id) {
        [$status, $tariff, $coop, $reason] = $expected[$code];
        $want = $status === null ? null : ($status === 'a_retirer' ? ['statut' => 'a_retirer']
            : ['email' => get_userdata($id)->user_email, 'statut' => $status, 'cooperateur' => $coop,
                'tarif' => $tariff, 'newsletters' => ['principale'],
                'personnalisation' => $code === 'A-CARTE' ? ['fictif' => ['choix' => ['a'], 'date_utc' => $date]] : []]);
        $actual[$code] = ContactBrevo::fiche((int)$id);
        $check('profil_' . $code, $actual[$code] === ['fiche' => $want, 'raison' => $reason]);
    }
    $check('reglages_present', method_exists(ContactBrevo::class, 'reglages'));
    ContactBrevo::reglages();
    $check('reglage_tarif_enregistre', get_registered_settings()[ContactBrevo::TARIFS]['default'] === []);
    $check('tarif_invalide_ferme', ContactBrevo::tarifs(['0' => 'normal']) === [] && ContactBrevo::tarifs(['192' => '<script>']) === [] && ContactBrevo::tarifs('mauvais') === []);
    $check('tarif_map_valide', ContactBrevo::tarifs(['192' => 'normal-1']) === [192 => 'normal-1']);
    $check('ecran_present', method_exists(ContactBrevo::class, 'page'));
    wp_set_current_user((int)$users['E-ABO']);
    $_SERVER['REQUEST_METHOD'] = 'GET';
    $_GET['compte'] = (string)$users['A-CARTE'];
    ob_start(); ContactBrevo::page(); $html = ob_get_clean();
    $check('ecran_fiche_et_totaux', str_contains($html, 'data-imagine-brevo') && str_contains($html, 'data-brevo-fiche') && str_contains($html, 'data-brevo-total="abonne"'));
    $check('ecran_aucun_POST_script', !str_contains($html, 'method="post"') && !str_contains($html, '<script'));
    $check('aucune_ecriture_SQL', $writes === []);
    $check('aucun_sortant', $outgoing === []);
} finally {
    remove_filter('query', $guard, PHP_INT_MAX);
    remove_filter('pre_http_request', $http, PHP_INT_MAX);
    remove_filter('pre_wp_mail', $mail, PHP_INT_MAX);
}
// Après le positif littéral ci-dessus, retrait du consentement DISTINCT uniquement.
update_user_meta($users['A-CARTE'], Personnalisation::CONSENTEMENT, ['accord' => false, 'date_utc' => $date]);
add_filter('query', $guard, PHP_INT_MAX);
add_filter('pre_http_request', $http, PHP_INT_MAX);
add_filter('pre_wp_mail', $mail, PHP_INT_MAX);
try {
    $negative = ContactBrevo::fiche((int)$users['A-CARTE']);
    $check('consentement_distinct_retire_attributs_absents', $negative['fiche']['personnalisation'] === []);
    $raw = file_get_contents(WP_PLUGIN_DIR . '/imagine-site/ContactBrevo.php');
    $mutant = str_replace('final class ContactBrevo', 'final class ContactBrevoC29Mutant', $raw);
    $mutant = str_replace('Personnalisation::attributsConnecteur($id)', 'Personnalisation::reponses($id)', $mutant, $hits);
    $check('mutation_source_unique', $hits === 1);
    eval(substr($mutant, 5));
    $leak = Imagine\Site\ContactBrevoC29Mutant::fiche((int)$users['A-CARTE']);
    $check('mutation_temoin_absence_refusee', $leak['fiche']['personnalisation'] !== [] && $negative['fiche']['personnalisation'] === []);
    foreach (['imagine_extraire_abonnes', 'imagine_gerer_echeances'] as $cap) {
        $deny = static function (array $caps) use ($cap): array { $caps[$cap] = false; return $caps; };
        add_filter('user_has_cap', $deny, PHP_INT_MAX);
        $check('droit_C19_revoque_' . $cap, !Imagine\Site\TableauBordAdmin::autorise());
        remove_filter('user_has_cap', $deny, PHP_INT_MAX);
    }
    $check('droit_C19_referent', Imagine\Site\TableauBordAdmin::autorise());
    $faultHits = 0;
    $fault = static function () use (&$faultHits): never { $faultHits++; throw new RuntimeException('Essai source'); };
    add_filter('woocommerce_get_subscriptions_query_args', $fault, PHP_INT_MAX);
    ob_start(); ContactBrevo::page(); $faultHtml = ob_get_clean();
    remove_filter('woocommerce_get_subscriptions_query_args', $fault, PHP_INT_MAX);
    $check('source_absente_aucun_faux_zero', $faultHits > 0 && str_contains($faultHtml, 'data-brevo-indisponible') && !str_contains($faultHtml, 'data-brevo-total'));
    $caught = false;
    try { update_option('imagine_c29_interdit', 'interdit', false); } catch (RuntimeException) { $caught = true; }
    $check('temoin_ecriture_interceptee', $caught && count($writes) === 1);
    $writes = [];
    try { wp_remote_get('https://example.invalid/'); } catch (RuntimeException) {}
    try { wp_mail('fictif@example.org', 'FICTIF', 'FICTIF'); } catch (RuntimeException) {}
    $check('temoins_HTTP_mail_bloques_avant_transport', $outgoing === ['http', 'mail']);
    $outgoing = [];
} finally {
    remove_filter('query', $guard, PHP_INT_MAX);
    remove_filter('pre_http_request', $http, PHP_INT_MAX);
    remove_filter('pre_wp_mail', $mail, PHP_INT_MAX);
}
// Relations temporaires directement dans le magasin natif constaté, sans hook
// d'enregistrement WCS (son invalidation de rapport s'exécute après ROLLBACK).
global $wpdb;
$giftSub = (int)$fixture['subscriptions']['A-CARTE'];
$hpos = \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled();
$table = $hpos ? $wpdb->prefix . 'wc_orders_meta' : $wpdb->postmeta;
$ownerKey = $hpos ? 'order_id' : 'post_id';
$check('relation_gift_initialement_absente', !wcs_get_subscription($giftSub)->meta_exists('_recipient_user'));
$wpdb->insert($table, [$ownerKey => $giftSub, 'meta_key' => '_recipient_user', 'meta_value' => (string)$users['P-OFFERT']]);
wp_cache_flush();
$check('relation_native_gift_relue', (string)wcs_get_subscription($giftSub)->get_meta('_recipient_user') === (string)$users['P-OFFERT']);
$check('beneficiaire_offert_inconnu', ContactBrevo::fiche((int)$users['P-OFFERT'])['fiche']['statut'] === 'inconnu');
$wpdb->delete($table, [$ownerKey => $giftSub, 'meta_key' => '_recipient_user']);
wp_cache_flush();
update_option('imagine_acces_plans', [$fixture['plan'] => 'groupe'], false);
$membership = (int)$fixture['memberships']['P-SOL-OK'];
global $wpdb;
$wpdb->update($wpdb->posts, ['post_author' => $users['P-BENEF']], ['ID' => $membership]);
clean_post_cache($membership);
update_post_meta($membership, '_subscription_id', (string)$fixture['subscriptions']['A-PAPIER']);
$check('beneficiaire_groupe_inconnu', ContactBrevo::fiche((int)$users['P-BENEF'])['fiche']['statut'] === 'inconnu');
$check('payeur_pas_beneficiaire_deduit', ContactBrevo::fiche((int)$users['A-PAPIER'])['fiche']['statut'] === 'abonne');
wp_set_current_user(0);
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'profils' => $actual, 'writes' => $writes, 'outgoing' => $outgoing,
    'mutation' => ['positive' => $actual['A-CARTE']['fiche']['personnalisation'], 'negative' => $negative['fiche']['personnalisation'], 'leak_mutant' => $leak['fiche']['personnalisation']], 'membership_restored_by_rollback' => $membership]);
