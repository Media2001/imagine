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
$copy = get_post(82);
$copy->post_content = 'CONTENU_FICTIF_RESERVE_NE_JAMAIS_EXTRAIRE';
$check('resume_vide_pas_corps', PageArticle::resume($copy) === '');
$check('pas_cta_paywall', !PageArticle::appel(['complet' => false, 'motif' => 'anonyme']));
$check('cta_acheteur', PageArticle::appel(['complet' => true, 'motif' => 'numero_achete']));
$check('pas_cta_abonne', !PageArticle::appel(['complet' => true, 'motif' => 'abonnement_actif']));
wp_set_current_user((int)$f['users']['A-PAPIER']);
$check('abonne_natif_actif', !PageArticle::appel(Imagine\Site\Paywall::decision(get_post(14))));
$uid = get_current_user_id();
$members = wc_memberships_get_user_memberships($uid, ['status' => 'any']);
$member = $members[0];
$member->update_status('complimentary');
Imagine\Site\Paywall::invalidate();
$gift = Imagine\Site\Paywall::decision(get_post(14));
$check('complimentary_natif_sans_appel', $gift['complet'] && in_array($gift['motif'], ['abonnement_actif', 'offert_actif'], true) && !PageArticle::appel($gift));
$subs = wcs_get_users_subscriptions($uid);
$sub = reset($subs);
$sub->update_dates(['end' => '2030-12-25 18:01:50']);
$sub->set_status('pending-cancel');$sub->save();
$member->update_status('pending');
update_post_meta($member->get_id(), '_end_date', '2031-01-01 00:00:00');
$clock = new ReflectionProperty(Imagine\Site\Paywall::class, 'requestInstant');
$oldClock = $clock->getValue();
try {
    foreach (['2030-12-25 18:01:49' => true, '2030-12-25 18:01:50' => false, '2030-12-25 18:01:51' => false] as $instant => $open) {
        $clock->setValue(null, new DateTimeImmutable($instant, new DateTimeZone('UTC')));
        Imagine\Site\Paywall::invalidate();
        $decision = Imagine\Site\Paywall::decision(get_post(14));
        $check('pending_cancel_natif_' . $instant, $decision['complet'] === $open && !PageArticle::appel($decision) && $decision['motif'] === ($open ? 'abonnement_actif' : 'expire'));
    }
} finally { $clock->setValue(null, $oldClock);Imagine\Site\Paywall::invalidate(); }
wp_set_current_user((int)$f['users']['P-NUMERO']);
$check('acheteur_pas_abonne', PageArticle::appel(Imagine\Site\Paywall::decision(get_post(14))));
wp_set_current_user(0);
$check('anonyme_pas_abonne', !PageArticle::appel(Imagine\Site\Paywall::decision(get_post(14))));
$old = get_post_meta($article->ID, PageArticle::SIGNATURE, true);
wp_set_current_user((int)get_users(['role' => 'administrator', 'number' => 1])[0]->ID);
$_POST = ['imagine_b16_nonce' => wp_create_nonce('imagine_b16'), PageArticle::SIGNATURE => wp_slash('FICTIF Journaliste \\ Essai')];
PageArticle::sauver($article->ID);
$check('signature_antislash_relue', get_post_meta($article->ID, PageArticle::SIGNATURE, true) === 'FICTIF Journaliste \\ Essai');
$_POST[PageArticle::SIGNATURE] = '';
PageArticle::sauver($article->ID);
$check('signature_effacee_relue', get_post_meta($article->ID, PageArticle::SIGNATURE, true) === '');
// Seul effet différé hors transaction : reconstruction des caches de rapports WCS.
// Neutralisé dans ce processus de recette, pas dans le code livré ni sur le site.
$check('rapport_cache_differe_ne_sort_pas_du_rollback', remove_action('shutdown', ['WCS_Report_Cache_Manager', 'schedule_cache_updates'], 10));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
