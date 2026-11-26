<?php

declare(strict_types=1);

namespace Imagine\Demo\C21;

use Imagine\Site\{Justificatifs, Decouverte, EnvoiNatif};

if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('C21 : cible fictive unique requise.');
}
require_once ABSPATH . 'wp-admin/includes/privacy-tools.php';
require_once ABSPATH . 'wp-admin/includes/user.php';
$phase = $phase ?? 'registration';
if ($phase === 'registration') {
    $e = apply_filters('wp_privacy_personal_data_exporters', []);
    $r = apply_filters('wp_privacy_personal_data_erasers', []);
    echo wp_json_encode(['exporter' => isset($e['imagine-site']), 'eraser' => isset($r['imagine-site'])]);
    return;
}
$f = get_option('imagine_c21_fixture', null);
if ($phase === 'setup') {
    if ($f !== null || get_user_by('login', 'imagine-c21-fictif')) {
        throw new \RuntimeException('Fixture C21 déjà présente : nettoyage explicite requis.');
    }
    $id = wp_insert_user(['user_login' => 'imagine-c21-fictif', 'user_pass' => wp_generate_password(48),
        'user_email' => 'c21-sans-email@compte.invalid', 'display_name' => 'C21 PERSONNE FICTIVE',
        'first_name' => 'C21', 'last_name' => 'FICTIF', 'role' => 'customer']);
    if (is_wp_error($id)) { throw new \RuntimeException('Création fictive refusée.'); }
    $f = ['user' => $id, 'options' => [], 'orders' => [], 'requests' => []];
    add_option('imagine_c21_fixture', $f, '', false);
    update_user_meta($id, 'imagine_sans_email', '1');
    update_user_meta($id, 'imagine_email_confirme', '1');
    $o = wc_create_order(['customer_id' => $id]);
    $o->set_billing_email('c21-sans-email@compte.invalid');
    $o->set_shipping_first_name('C21'); $o->set_shipping_last_name('FICTIF');
    $o->set_shipping_address_1('21 Rue FICTIVE'); $o->set_shipping_postcode('0000');
    $o->set_shipping_city('FICTIF'); $o->set_shipping_country('BE');
    $item = new \WC_Order_Item_Product(); $item->set_name('Numéro C21 fictif');
    $item->set_quantity(1); $item->add_meta_data('_imagine_achat_numero_id', '167');
    $o->add_item($item); $o->update_meta_data('_imagine_envoi_bloc_debut', '2026-01-01 00:00:00');
    $o->update_meta_data('_payment_method_token', 'C21-SECRET-TOKEN');
    $o->add_order_note('C21-NOTE-INTERNE-INTERDITE'); $o->save();
    $f['orders'][] = $o->get_id(); update_option('imagine_c21_fixture', $f, false);
    $s = wcs_create_subscription(['customer_id' => $id, 'order_id' => $o->get_id(), 'status' => 'active',
        'billing_period' => 'year', 'billing_interval' => 1, 'start_date' => '2026-01-01 00:00:00']);
    if (is_wp_error($s)) { throw new \RuntimeException('Abonnement fictif refusé.'); }
    $s->set_address($o->get_address('shipping'), 'shipping');
    $s->update_meta_data('_imagine_acces_grace_debut', '2026-11-01 00:00:00');
    $s->update_meta_data('_imagine_acces_grace_fin', '2026-12-01 00:00:00'); $s->save();
    $f['orders'][] = $s->get_id(); update_option('imagine_c21_fixture', $f, false);
    $record = EnvoiNatif::relever($s);
    $put = static function (string $key, mixed $v) use (&$f): void {
        if (!add_option($key, $v, '', false)) { throw new \RuntimeException('Collision fixture.'); }
        $f['options'][] = $key; update_option('imagine_c21_fixture', $f, false);
    };
    $put(Decouverte::key($id), ['debut' => '2026-11-01 00:00:00', 'reglages' => Decouverte::defauts(), 'articles' => [167]]);
    // Exercer une décision complète puis un nouveau dépôt : audit + fichier en attente sur le même compte.
    $put(Justificatifs::PREFIX . $id, ['categorie' => 'à préciser', 'decision' => 'valide', 'fin' => '2027-12-31']);
    $fixturePath = WP_PLUGIN_DIR . '/imagine-site/tests/fixtures/c17-fictif.pdf';
    $bytes = is_file($fixturePath) ? file_get_contents($fixturePath) : false;
    if (!$bytes) { $bytes = "%PDF-1.4\nC21 FICTIF\n%%EOF\n"; }
    $doc = Justificatifs::recevoir($id, 'à préciser', $bytes, Justificatifs::version(Justificatifs::etat($id)));
    $f['doc'] = Justificatifs::chemin($doc); $f['document_sha256'] = hash('sha256', $bytes);
    update_option('imagine_c21_fixture', $f, false);
    $put(EnvoiNatif::GEL . 'C21-FICTIF', ['version' => 1, 'numero' => '167',
        'calendrier' => get_option(EnvoiNatif::CALENDRIER), 'observations' => [$record],
        'cloture' => '2026-01-05T00:00:00+00:00', 'blocs' => [(string) $s->get_id() => []]]);
    // Une autre personne sur une observation partagée, jamais révélée ni retirée.
    $shared = $record; $shared['donnees']['user'] = '999999';
    $shared['donnees']['id'] = '999999'; $shared['donnees']['destinataire'] = 'C21-AUTRE-PERSONNE';
    $shared['donnees']['beneficiaires'] = [['id' => (string) $id, 'nom' => 'C21 BENEFICIAIRE', 'rue' => '21 Rue FICTIVE'],
        ['id' => '999998', 'nom' => 'C21-AUTRE-BENEFICIAIRE']];
    $shared['donnees']['relation_native'] = [['user_id' => $id], ['user_id' => 999998]];
    $put(EnvoiNatif::RELEVE . 'C21-PARTAGE', $shared);
    $token = str_repeat('a', 32);
    $f['draft'] = 'imagine_c16_brouillon_1_' . $token;
    set_transient($f['draft'], ['qui' => 1, 'token' => $token, 'client' => ['mode' => 'existant', 'id' => $id],
        'commande' => ['adresse' => ['first_name' => 'C21', 'last_name' => 'FICTIF', 'address_1' => '21 Rue FICTIVE'],
            'produit' => 0, 'mode_paiement' => 'bacs'], 'etape' => 3, 'empreinte' => 'C21-TOKEN-PRIVE'], HOUR_IN_SECONDS);
    update_option('imagine_c21_fixture', $f, false);
    echo wp_json_encode(['user' => $id, 'email' => get_userdata($id)->user_email, 'orders' => $f['orders'], 'document_sha256' => $f['document_sha256']]);
    return;
}
if (!is_array($f) || !get_userdata($f['user'])) { throw new \RuntimeException('Fixture absente.'); }
if ($phase === 'inspect') {
    $o = [];
    $id = (int) $f['user'];
    foreach (['imagine_sans_email', 'imagine_email_confirme'] as $key) { $o[$key] = get_user_meta($id, $key, true); }
    $o['decouverte'] = get_option(Decouverte::key($id), null);
    $o['justificatif'] = get_option(Justificatifs::PREFIX . $id, null);
    clearstatcache(true, $f['doc']); $o['document_exists'] = file_exists($f['doc']);
    $o['draft_exists'] = get_transient($f['draft']) !== false;
    global $wpdb;
    $o['residual_options'] = [];
    foreach ($wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE 'imagine_envoi_%' OR option_name LIKE 'imagine_reglages_journal_%'", ARRAY_A) as $row) {
        $v = maybe_unserialize($row['option_value']);
        if (str_contains($row['option_name'], 'C21') || (($v['option'] ?? '') === Justificatifs::PREFIX . $id)
            || (isset($v['donnees']) && (int) ($v['donnees']['user'] ?? 0) === $id)) { $o['residual_options'][$row['option_name']] = $v; }
    }
    foreach ($f['orders'] as $oid) { $object = wc_get_order($oid); $o['native'][$oid] = [$object->get_status(), $object->get_customer_id()]; }
    echo wp_json_encode($o); return;
}
if ($phase === 'cleanup') {
    // Exact owned entities only. No catalog, profile, email or global seed.
    foreach ($f['requests'] as $rid) {
        $name = get_post_meta($rid, '_export_file_name', true);
        if ($name && basename($name) === $name) { wp_delete_file(wp_privacy_exports_dir() . $name); }
        wp_delete_post($rid, true);
    }
    foreach ($f['orders'] as $oid) { $object = wc_get_order($oid); if ($object && $object->get_customer_id() === (int) $f['user']) { $object->delete(true); } }
    // Remove only observations tied to the disposable subscription and explicit fixture options/audit.
    global $wpdb;
    foreach ($wpdb->get_col($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s", $wpdb->esc_like(EnvoiNatif::RELEVE . ($f['orders'][1] ?? 0) . '_') . '%')) as $key) { delete_option($key); }
    foreach ($wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE 'imagine_reglages_journal_%'", ARRAY_A) as $row) {
        $v = maybe_unserialize($row['option_value']);
        if (($v['option'] ?? '') === Justificatifs::PREFIX . $f['user']) { delete_option($row['option_name']); }
    }
    foreach ($f['options'] as $key) { delete_option($key); }
    delete_transient($f['draft']);
    $removed = wp_delete_user($f['user']);
    delete_option('imagine_c21_fixture');
    echo wp_json_encode(['deleted' => $removed && !get_userdata($f['user']), 'manifest_absent' => get_option('imagine_c21_fixture', null) === null,
        'document_absent' => !file_exists($f['doc'])]); return;
}
throw new \RuntimeException('Phase inconnue.');
