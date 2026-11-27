<?php

declare(strict_types=1);

use Imagine\Site\PageArticle;

if (!class_exists(PageArticle::class)) {
    throw new RuntimeException('B16 page article absente');
}
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) { throw new RuntimeException($name); }
};
$f = get_option('imagine_c09_fixture');
$article = get_posts(['post_type' => 'post', 'numberposts' => 1])[0];
$check('resume_saisi_sans_generation', PageArticle::resume($article) === trim($article->post_excerpt));
$copy = clone $article;
$copy->post_excerpt = '';
$copy->post_content = 'CONTENU_FICTIF_RESERVE_NE_JAMAIS_EXTRAIRE';
$check('resume_vide_pas_corps', PageArticle::resume($copy) === '');
$check('pas_cta_paywall', !PageArticle::appel(['complet' => false], false));
$check('cta_acheteur', PageArticle::appel(['complet' => true], false));
$check('pas_cta_abonne', !PageArticle::appel(['complet' => true], true));
wp_set_current_user((int)$f['users']['A-PAPIER']);
$check('abonne_natif_actif', PageArticle::abonne());
wp_set_current_user((int)$f['users']['P-NUMERO']);
$check('acheteur_pas_abonne', !PageArticle::abonne());
wp_set_current_user(0);
$check('anonyme_pas_abonne', !PageArticle::abonne());
$old = get_post_meta($article->ID, PageArticle::SIGNATURE, true);
$_POST = ['imagine_b16_nonce' => wp_create_nonce('imagine_b16'), PageArticle::SIGNATURE => wp_slash('FICTIF Journaliste \\ Essai')];
wp_set_current_user(1);
PageArticle::sauver($article->ID);
$check('signature_antislash_relue', get_post_meta($article->ID, PageArticle::SIGNATURE, true) === 'FICTIF Journaliste \\ Essai');
$_POST[PageArticle::SIGNATURE] = '';
PageArticle::sauver($article->ID);
$check('signature_effacee_relue', get_post_meta($article->ID, PageArticle::SIGNATURE, true) === '');
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
