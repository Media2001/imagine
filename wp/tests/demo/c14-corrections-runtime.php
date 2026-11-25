<?php
/** Complément natif C14-01/02, mêmes décisions que les parcours HTTP. */
declare(strict_types=1);
use Imagine\Site\AchatsNumeros;
use Imagine\Demo\C14\Corrections as C;
require_once WP_CONTENT_DIR . '/imagine-demo-build/c14-corrections-fixture.php';
$checks = [];
$policy = get_option(AchatsNumeros::REMBOURSEMENT, null);
try {
    foreach (['commande', 'ligne'] as $mode) {
        update_option(AchatsNumeros::REMBOURSEMENT, $mode);
        $checks[$mode . '_option_relue'] = get_option(AchatsNumeros::REMBOURSEMENT) === $mode;
        foreach (['ventile', 'non_ventile', 'total'] as $kind) {
            $f = C\seed();
            try {
                $checks[$mode . '_' . $kind . '_avant_articles_PDF'] = C\decisions($f) === ['a' => [true, true], 'b' => [true, true]];
                $r = C\refund($f, $kind);
                $checks[$mode . '_' . $kind . '_remboursement_natif_zero'] = $r['zero_sans_passerelle']
                    && $r['lignes'] === ($kind === 'total' ? 2 : ($kind === 'ventile' ? 1 : 0))
                    && $r['statut'] === ($kind === 'total' ? 'refunded' : 'processing');
                $expected = $kind === 'total' || $mode === 'commande' ? ['a' => [false, false], 'b' => [false, false]]
                    : ['a' => [$kind !== 'ventile', $kind !== 'ventile'], 'b' => [true, true]];
                $checks[$mode . '_' . $kind . '_apres_articles_PDF_meme_requete'] = C\decisions($f) === $expected;
            } finally {
                foreach (C\cleanup($f) as $key => $value) { $checks[$mode . '_' . $kind . '_' . $key] = $value; }
            }
        }
    }
    $f = C\seed();
    try {
        C\owned($f, $f['order'], true);
        $o = wc_get_order($f['order']); $o->remove_item($f['items']['b']); $o->save();
        $expected = ['a' => [true, true], 'b' => [false, false]];
        $checks['instantane_seul_numero_acquis'] = C\decisions($f) === $expected;
        C\owned($f, $f['products']['a']);
        $p = wc_get_product($f['products']['a']);
        $p->update_meta_data(AchatsNumeros::PRODUIT, $f['issues']['b']); $p->save();
        $checks['catalogue_reaffecte_A_conserve_B_ferme'] = C\decisions($f) === $expected;
        // Un achat suivant prend B, sans changer l'instantané de la première ligne.
        $next = $o->add_product($p, 1, ['subtotal' => '0', 'total' => '0']); $o->save();
        $checks['achat_suivant_B_seulement'] = (int) wc_get_order_item_meta($next, AchatsNumeros::LIGNE, true) === $f['issues']['b']
            && (int) wc_get_order_item_meta($f['items']['a'], AchatsNumeros::LIGNE, true) === $f['issues']['a'];
        $o->remove_item($next); $o->save();
        $p->delete_meta_data(AchatsNumeros::PRODUIT); $p->save();
        $checks['catalogue_vide_A_conserve_B_ferme'] = C\decisions($f) === $expected;
        $p->delete(true);
        $checks['catalogue_supprime_A_conserve_B_ferme'] = C\decisions($f) === $expected;
        C\owned($f, $f['issues']['a']);
        wp_update_post(['ID' => $f['issues']['a'], 'post_status' => 'draft']);
        $checks['numero_acquis_depublie_articles_PDF_fermes'] = C\decisions($f) === ['a' => [false, false], 'b' => [false, false]];
        wp_update_post(['ID' => $f['issues']['a'], 'post_status' => 'publish']);
        $checks['publication_retablie_droit_retabli'] = C\decisions($f) === $expected;
        $item = wc_get_order($f['order'])->get_item($f['items']['a']);
        $item->delete_meta_data(AchatsNumeros::LIGNE); $item->save();
        $checks['instantane_retire_pas_de_retrooctroi'] = C\decisions($f) === ['a' => [false, false], 'b' => [false, false]]
            && !$item->meta_exists(AchatsNumeros::LIGNE);
        $item->update_meta_data(AchatsNumeros::LIGNE, $f['issues']['a']); $item->save();
        $checks['instantane_retabli_apres_produit_supprime'] = C\decisions($f) === $expected;
        wp_delete_post($f['issues']['a'], true);
        $old = get_current_user_id(); wp_set_current_user($f['user']);
        try {
            $checks['numero_acquis_supprime_article_ferme'] = !\Imagine\Site\Paywall::decision(get_post($f['articles']['a']['id']))['complet'];
        } finally { wp_set_current_user($old); }
    } finally {
        foreach (C\cleanup($f) as $key => $value) { $checks['catalogue_' . $key] = $value; }
    }
} finally {
    if ($policy === null) { delete_option(AchatsNumeros::REMBOURSEMENT); }
    else { update_option(AchatsNumeros::REMBOURSEMENT, $policy); }
}
$checks['option_restauree_exactement'] = get_option(AchatsNumeros::REMBOURSEMENT, null) === $policy;
echo wp_json_encode($checks);
if (in_array(false, $checks, true)) { WP_CLI::halt(1); }
