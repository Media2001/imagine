<?php
/** Objets C14 jetables, zéro euro, aucun accès fournisseur ni transport financier. */
declare(strict_types=1);
namespace Imagine\Demo\C14\Corrections;

use Imagine\Site\AchatsNumeros;
use Imagine\Site\Paywall;

require_once WP_CONTENT_DIR . '/imagine-demo-build/c14-profil.php';

function owned(array $f, int $id, bool $order = false): void
{
    \Imagine\Demo\C14\guard();
    $value = $order ? wc_get_order($id)?->get_meta('_imagine_c14_fixture') : get_post_meta($id, '_imagine_c14_fixture', true);
    if ($value !== $f['token']) { throw new \RuntimeException('Objet C14 non possédé : ' . $id); }
}

function seed(): array
{
    \Imagine\Demo\C14\guard();
    $f = ['token' => wp_generate_uuid4(), 'posts' => [], 'orders' => [], 'issues' => [], 'articles' => [], 'products' => [], 'items' => []];
    $f['user'] = (int) get_option('imagine_c09_fixture')['users']['P-NUMERO'];
    $source = (int) get_option('imagine_demo_manifest')['demo-2026-t1'];
    try {
        foreach (['a', 'b'] as $key) {
            $issue = wp_insert_post(['post_type' => 'imagine_numero', 'post_status' => 'publish',
                'post_title' => 'Numéro FICTIF correction C14 ' . $f['token'] . $key,
                'post_date' => '2000-01-01 00:00:00', 'post_date_gmt' => '2000-01-01 00:00:00',
                'meta_input' => ['_imagine_c14_fixture' => $f['token'], 'imagine_sortie' => '2000-01-01',
                    '_imagine_pdf_blob' => get_post_meta($source, '_imagine_pdf_blob', true)]], true);
            if (is_wp_error($issue)) { throw new \RuntimeException('Numéro C14 impossible'); }
            $f['posts'][] = $issue; $f['issues'][$key] = $issue;
            $witness = 'TEMOIN_C14_CORRECTION_' . str_replace('-', '', $f['token']) . '_' . $key;
            $article = wp_insert_post(['post_type' => 'post', 'post_status' => 'publish',
                'post_title' => 'Article FICTIF correction C14 ' . $f['token'] . $key,
                'post_date' => '2000-01-01 00:00:00', 'post_date_gmt' => '2000-01-01 00:00:00',
                'post_content' => '<p>Texte entièrement fictif.</p><p>' . $witness . '</p>', 'post_excerpt' => 'Extrait public fictif.',
                'meta_input' => ['_imagine_c14_fixture' => $f['token'], 'imagine_reserve' => '1', 'imagine_numero_id' => $issue]], true);
            if (is_wp_error($article)) { throw new \RuntimeException('Article C14 impossible'); }
            $f['posts'][] = $article;
            $f['articles'][$key] = ['id' => $article, 'path' => wp_parse_url(get_permalink($article), PHP_URL_PATH), 'witness' => $witness];
            $p = new \WC_Product_Simple();
            $p->set_name('Produit FICTIF correction C14 ' . $f['token'] . $key);
            $p->set_status('private'); $p->set_catalog_visibility('hidden'); $p->set_virtual(true);
            $p->set_tax_status('none'); $p->set_regular_price('0'); $p->set_price('0');
            $p->update_meta_data('_imagine_c14_fixture', $f['token']);
            $p->update_meta_data(AchatsNumeros::PRODUIT, $issue); $p->save();
            $f['posts'][] = $p->get_id(); $f['products'][$key] = $p->get_id();
        }
        $o = wc_create_order(['customer_id' => $f['user'], 'status' => 'pending', 'created_via' => 'admin']);
        if (is_wp_error($o)) { throw new \RuntimeException('Commande C14 impossible'); }
        $f['order'] = $o->get_id(); $f['orders'][] = $o->get_id();
        $o->update_meta_data('_imagine_c14_fixture', $f['token']);
        $o->set_payment_method(''); $o->set_transaction_id('');
        foreach ($f['products'] as $key => $id) {
            $f['items'][$key] = $o->add_product(wc_get_product($id), 1, ['subtotal' => '0', 'total' => '0']);
        }
        $o->calculate_totals(false); $o->set_status('processing');
        $o->set_date_paid(time() - DAY_IN_SECONDS); $o->save();
        return $f;
    } catch (\Throwable $e) {
        cleanup($f);
        throw $e;
    }
}

function refund(array &$f, string $kind): array
{
    owned($f, $f['order'], true);
    $o = wc_get_order($f['order']);
    if ($o->get_total() != 0 || $o->get_payment_method() !== '' || $o->get_transaction_id() !== '') {
        throw new \RuntimeException('Commande non nulle ou financière refusée');
    }
    $lines = [];
    foreach ($f['items'] as $key => $id) {
        if ($kind === 'total' || ($kind === 'ventile' && $key === 'a')) {
            $lines[$id] = ['qty' => $kind === 'total' ? 1 : 0.5, 'refund_total' => 0, 'refund_tax' => []];
        }
    }
    // Sur zéro euro, Woo classerait un remboursement non ventilé comme total (0=0).
    // Ce filtre natif ne fait que désigner notre scénario partiel, pour ce seul objet.
    $partial = static fn ($value, $id) => $id === $f['order'] && $kind !== 'total' ? true : $value;
    add_filter('woocommerce_order_is_partially_refunded', $partial, 10, 2);
    try {
        $r = wc_create_refund(['order_id' => $f['order'], 'amount' => 0, 'line_items' => $lines,
            'refund_payment' => false, 'restock_items' => false, 'reason' => 'FICTIF C14 ' . $f['token'] . ' ' . $kind]);
    } finally {
        remove_filter('woocommerce_order_is_partially_refunded', $partial, 10);
    }
    if (is_wp_error($r)) { throw new \RuntimeException('Remboursement C14 refusé : ' . $r->get_error_message()); }
    $f['orders'][] = $r->get_id();
    $r->update_meta_data('_imagine_c14_fixture', $f['token']); $r->save();
    $read = wc_get_order($r->get_id());
    return ['id' => $read->get_id(), 'zero_sans_passerelle' => $read->get_amount() == 0 && !$read->get_refunded_payment(),
        'statut' => wc_get_order($f['order'])->get_status(), 'lignes' => count($read->get_items('line_item'))];
}

function decisions(array $f): array
{
    $old = get_current_user_id();
    wp_set_current_user($f['user']);
    try {
        $out = [];
        foreach ($f['issues'] as $key => $id) {
            $out[$key] = [Paywall::decision(get_post($f['articles'][$key]['id']))['complet'], Paywall::decisionPdf(get_post($id))['complet']];
        }
        return $out;
    } finally { wp_set_current_user($old); }
}

function cleanup(array $f): array
{
    \Imagine\Demo\C14\guard();
    foreach (array_reverse($f['orders']) as $id) {
        if (wc_get_order($id)) {
            owned($f, $id, true);
            wc_get_order($id)->delete(true);
        }
    }
    foreach (array_reverse($f['posts']) as $id) {
        if (get_post($id)) { owned($f, $id); wp_delete_post($id, true); }
    }
    return ['commandes_absentes' => !array_filter($f['orders'], static fn ($id) => (bool) wc_get_order($id)),
        'posts_absents' => !array_filter($f['posts'], static fn ($id) => (bool) get_post($id))];
}
