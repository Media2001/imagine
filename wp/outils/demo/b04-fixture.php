<?php

declare(strict_types=1);

// Fictive B04 objects only. No order, rights, gateway, mail or existing fixture changes.
if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || rtrim(home_url(), '/') !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('B04 requires the named local fictive demo.');
}
$action = $GLOBALS['imagine_b04_action'] ?? 'inspect';
$fixture = get_option('imagine_b04_fixture', []);
if (!is_array($fixture)) {
    throw new RuntimeException('B04 manifest invalid.');
}
$owned = static function (int $id, string $marker, string $type): WP_Post {
    $post = get_post($id);
    if (!$post || $post->post_type !== $type || get_post_meta($id, '_imagine_b04_fixture', true) !== $marker) {
        throw new RuntimeException('B04 exact ownership refused.');
    }
    return $post;
};
if ($action === 'product') {
    $manifest = get_option('imagine_demo_manifest');
    if (($manifest['demo-2026-t1'] ?? 0) !== 11 || get_post_type(11) !== 'imagine_numero') {
        throw new RuntimeException('B04 existing issue identity refused.');
    }
    if (!empty($fixture['product'])) {
        $owned((int) $fixture['product'], 'product-v1', 'product');
    } else {
        if (get_page_by_path('b04-produit-fictif-numero-11', OBJECT, 'product')) {
            throw new RuntimeException('B04 slug collision refused.');
        }
        $product = new WC_Product_Simple();
        $product->set_name('FICTIF B04 — Numéro de démonstration 11 — 0 €');
        $product->set_slug('b04-produit-fictif-numero-11');
        $product->set_status('publish');
        $product->set_catalog_visibility('visible');
        $product->set_description('Produit fictif de démonstration B04, sans paiement réel. Aucun achat à effectuer.');
        $product->set_short_description('FICTIF B04 — témoin du parcours natif au numéro, sans passerelle ni commande.');
        $product->set_regular_price('0');
        $product->set_price('0');
        $product->set_virtual(true);
        $product->set_downloadable(false);
        $product->set_manage_stock(false);
        $product->set_stock_status('instock');
        $product->set_tax_status('none');
        $product->set_sold_individually(true);
        $product->update_meta_data('_imagine_b04_fixture', 'product-v1');
        $product->update_meta_data(Imagine\Site\AchatsNumeros::PRODUIT, 11);
        $fixture['product'] = $product->save();
        update_option('imagine_b04_fixture', $fixture, false);
    }
} elseif ($action === 'witness') {
    if (empty($fixture['witness'])) {
        if (get_page_by_path('b04-temoin-fictif-20-articles', OBJECT, 'imagine_numero')) {
            throw new RuntimeException('B04 witness slug collision refused.');
        }
        $id = wp_insert_post(wp_slash([
            'post_type' => 'imagine_numero', 'post_status' => 'publish',
            'post_title' => 'FICTIF B04 — témoin temporaire de vingt articles',
            'post_name' => 'b04-temoin-fictif-20-articles',
            'post_content' => '<p>Présentation fictive B04, uniquement pour la mesure des requêtes.</p>',
            'post_excerpt' => 'Témoin fictif temporaire B04, sans droit ajouté.',
            'meta_input' => ['_imagine_b04_fixture' => 'issue-v1', 'imagine_sortie' => '2000-01-01'],
        ]), true);
        if (is_wp_error($id)) {
            throw new RuntimeException('B04 witness creation failed.');
        }
        $fixture['witness'] = (int) $id;
        $fixture['articles'] = [];
        update_option('imagine_b04_fixture', $fixture, false);
    }
    $owned((int) $fixture['witness'], 'issue-v1', 'imagine_numero');
    for ($i = count($fixture['articles']) + 1; $i <= 20; $i++) {
        $slug = sprintf('b04-article-fictif-%02d', $i);
        if (get_page_by_path($slug, OBJECT, 'post')) {
            throw new RuntimeException('B04 article slug collision refused.');
        }
        $id = wp_insert_post(wp_slash([
            'post_type' => 'post', 'post_status' => 'publish', 'post_name' => $slug,
            'post_title' => sprintf('FICTIF B04 — article témoin %02d', $i),
            'post_content' => '<p>Corps réservé fictif B04, ne doit jamais être présent dans le sommaire.</p>',
            'post_excerpt' => 'Extrait public du témoin fictif B04.', 'menu_order' => $i,
            'meta_input' => ['_imagine_b04_fixture' => 'article-v1', 'imagine_numero_id' => $fixture['witness'],
                'imagine_reserve' => '1', 'imagine_decouverte' => '0'],
        ]), true);
        if (is_wp_error($id)) {
            throw new RuntimeException('B04 article creation failed.');
        }
        $fixture['articles'][] = (int) $id;
        update_option('imagine_b04_fixture', $fixture, false);
    }
} elseif ($action === 'cleanup-witness') {
    // Validate the complete ownership graph BEFORE any deletion. Never select by title/prefix.
    $issue = (int) ($fixture['witness'] ?? 0);
    if ($issue) {
        $owned($issue, 'issue-v1', 'imagine_numero');
        foreach ($fixture['articles'] as $id) {
            $owned((int) $id, 'article-v1', 'post');
            if ((int) get_post_meta($id, 'imagine_numero_id', true) !== $issue) {
                throw new RuntimeException('B04 witness relation drift.');
            }
        }
        foreach ($fixture['articles'] as $id) {
            if (!wp_delete_post((int) $id, true)) {
                throw new RuntimeException('B04 owned article deletion failed.');
            }
        }
        if (!wp_delete_post($issue, true)) {
            throw new RuntimeException('B04 owned issue deletion failed.');
        }
        unset($fixture['witness'], $fixture['articles']);
        update_option('imagine_b04_fixture', $fixture, false);
    }
} elseif ($action !== 'inspect') {
    throw new RuntimeException('B04 unknown action.');
}
$out = ['fixture' => get_option('imagine_b04_fixture', []), 'product' => null, 'witness' => null];
if (!empty($out['fixture']['product'])) {
    $id = (int) $out['fixture']['product'];
    $owned($id, 'product-v1', 'product');
    $product = wc_get_product($id);
    $out['product'] = ['id' => $id, 'status' => $product->get_status(), 'price' => $product->get_price(),
        'type' => $product->get_type(), 'virtual' => $product->is_virtual(), 'stock_managed' => $product->get_manage_stock(),
        'numero' => Imagine\Site\AchatsNumeros::numero($product), 'url' => $product->get_permalink()];
}
if (!empty($out['fixture']['witness'])) {
    $id = (int) $out['fixture']['witness'];
    $owned($id, 'issue-v1', 'imagine_numero');
    $articles = get_posts(['post_type' => 'post', 'post_status' => 'publish', 'numberposts' => -1,
        'meta_key' => 'imagine_numero_id', 'meta_value' => $id, 'orderby' => ['menu_order' => 'ASC', 'ID' => 'ASC']]);
    $out['witness'] = ['id' => $id, 'url' => get_permalink($id), 'articles' => wp_list_pluck($articles, 'ID')];
}
echo wp_json_encode($out);
