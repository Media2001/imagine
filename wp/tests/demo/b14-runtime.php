<?php

declare(strict_types=1);

use Imagine\Site\Accueil;

if (!class_exists(Accueil::class)) {
    throw new RuntimeException('B14 accueil absent');
}
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) {
        throw new RuntimeException($name);
    }
};
$issue = Accueil::numero();
$check('numero_regle_b04', $issue && $issue->ID === Imagine\Theme\imagine_issue_query(1)->posts[0]->ID);
$free = Accueil::libre($issue);
$check('reportage_designe_b04', $free && Imagine\Theme\imagine_access_status(Imagine\Site\Paywall::decisionListe($free))['code'] === 'libre');
if (Imagine\Theme\imagine_issue_product($issue->ID) === '') {
    $temporary = new WC_Product_Simple();
    $temporary->set_name('FICTIF B14 — produit de réception transactionnel');
    $temporary->set_status('publish');
    $temporary->set_catalog_visibility('hidden');
    $temporary->set_virtual(true);
    $temporary->set_regular_price('1.00');
    $temporary->set_price('1.00');
    $temporary->update_meta_data(Imagine\Site\AchatsNumeros::PRODUIT, (string)$issue->ID);
    $temporary->save();
}
ob_start();
Accueil::rendre();
$html = ob_get_clean();
preg_match_all('/data-b14-section="([^"]+)"/', $html, $found);
$check('ordre_huit_sections', $found[1] === ['numero', 'conversion', 'reportage', 'newsletter', 'thematiques', 'evenements', 'soutenir', 'cooperative']);
$check('ancre_thematiques_menu_conservee', str_contains($html, 'id="imagine-thematiques"'));
$check('partenaire_apres_cooperative', strpos($html, 'data-imagine-partenaire-mois=') > strpos($html, 'data-b14-section="cooperative"'));
$check('partenariat_conserve', str_contains($html, 'imagine-partnership-label') && str_contains($html, 'Partenariat'));
$check('une_image_prioritaire', substr_count($html, 'fetchpriority="high"') === 1 && substr_count($html, 'loading="eager"') === 1);
$check('pas_video_iframe', !preg_match('/<(video|iframe)\b/i', $html));
$check('pas_derniers_articles', !str_contains($html, 'Derniers articles') && !str_contains($html, 'imagine-latest-posts'));
$check('selection_evenements_bornee', Accueil::premiersEvenements([1, 2, 3, 4]) === [1, 2, 3]);
$check('newsletter_lien_seul', str_contains($html, '/nos-newsletters/') && !str_contains($html, '<form'));
$url = Imagine\Theme\imagine_issue_product($issue->ID);
$check('achat_positif_avant_retrait', $url !== '' && str_contains($html, 'data-b14-acheter'));
$product = get_posts(['post_type' => 'product', 'post_status' => 'publish', 'numberposts' => -1,
    'meta_key' => Imagine\Site\AchatsNumeros::PRODUIT, 'meta_value' => $issue->ID]);
$check('produit_natif_existe', count($product) > 0);
foreach ($product as $p) {
    wp_update_post(['ID' => $p->ID, 'post_status' => 'draft']);
    clean_post_cache($p->ID);
    $check('produit_retrait_relu_' . $p->ID, wc_get_product($p->ID)->get_status() === 'draft');
}
ob_start();
Accueil::rendre();
$without = ob_get_clean();
$check('achat_absent_hors_vente', !str_contains($without, 'data-b14-acheter'));
update_post_meta($free->ID, 'imagine_reserve', '1');
Imagine\Site\Paywall::invalidate();
$check('reportage_absent_si_aucun_libre', Accueil::libre($issue) === null);
ob_start();
Accueil::rendre();
$without = ob_get_clean();
$check('section_reportage_absente', !str_contains($without, 'data-b14-section="reportage"'));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
