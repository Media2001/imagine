<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085'
    || apply_filters('pre_wp_mail', null, []) !== false
    || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
    || WC()->payment_gateways()->get_available_payment_gateways() !== []) {
    throw new RuntimeException('C28 cible fictive refusée');
}
$f = get_option('imagine_c28_fixture', null);
if ($f === null) {
    if (get_page_by_path('c28-pack-thematique-fictif', OBJECT, 'product')) {
        throw new RuntimeException('C28 collision produit');
    }
    $issues = [11, 18, 25, 32];
    $articles = [];
    foreach ($issues as $id) {
        $posts = get_posts(['post_type' => 'post', 'post_status' => 'publish', 'numberposts' => 1,
            'meta_query' => [['key' => 'imagine_numero_id', 'value' => $id], ['key' => 'imagine_reserve', 'value' => '1']],
            'orderby' => 'ID', 'order' => 'ASC']);
        if (!$posts || !is_file(Imagine\Site\PdfNumero::path($id)) || !has_post_thumbnail($id)) {
            throw new RuntimeException('C28 prérequis numéro/article/PDF/couverture');
        }
        $articles[$id] = $posts[0]->ID;
    }
    global $wpdb;
    $actionsTable = $wpdb->prefix . 'actionscheduler_actions';
    $actionsBefore = $wpdb->get_col("SELECT action_id FROM $actionsTable");
    $p = new WC_Product_Simple();
    $p->set_name('C28 — Pack thématique entièrement fictif');
    $p->set_slug('c28-pack-thematique-fictif');
    $p->set_status('publish');
    $p->set_virtual(true);
    $p->set_catalog_visibility('visible');
    $p->set_tax_status('none');
    $p->set_regular_price('3.28');
    $p->set_price('3.28');
    $p->set_description('Démonstration fictive : trois anciens numéros, sans paiement réel.');
    $p->update_meta_data(Imagine\Site\PacksThematiques::PRODUIT, [11, 18, 25]);
    $p->update_meta_data('_imagine_c28_fictif', '1');
    $p->save();
    // Pas de travail de catalogue natif laissé en attente par la seule fixture.
    foreach ($wpdb->get_results("SELECT * FROM $actionsTable", ARRAY_A) as $row) {
        if (!in_array($row['action_id'], $actionsBefore, true)
            && $row['hook'] === 'woocommerce_run_product_attribute_lookup_update_callback'
            && $row['args'] === wp_json_encode([$p->get_id(), 1])
            && $row['status'] === 'pending' && $row['attempts'] === '0') {
            $wpdb->delete($wpdb->prefix . 'actionscheduler_logs', ['action_id' => $row['action_id']]);
            $wpdb->delete($actionsTable, ['action_id' => $row['action_id']]);
        }
    }
    $f = ['fictif' => true, 'product' => $p->get_id(), 'issues' => [11, 18, 25], 'fourth' => 32,
        'articles' => $articles, 'price_fictif' => '3.28'];
    update_option('imagine_c28_fixture', $f, false);
}
$p = wc_get_product($f['product']);
if (!$p || $p->get_meta('_imagine_c28_fictif') !== '1'
    || Imagine\Site\PacksThematiques::numeros($p) !== $f['issues']
    || get_option('imagine_c28_fixture') !== $f) {
    throw new RuntimeException('C28 fixture non relue');
}
echo wp_json_encode($f + ['url' => $p->get_permalink()]);
