<?php
/** Une vérification par exigence de droit, sans modifier les bibliothèques closes. */
declare(strict_types=1);

use Imagine\Site\Paywall;
use Imagine\Site\PdfNumero;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new RuntimeException('Cible C11 refusée.');
}
$checks = [];
$f = get_option('imagine_c08_fixture');
$manifest = get_option('imagine_demo_manifest');
$issue = get_post($manifest['demo-2026-t4']);
$user = get_current_user_id();
$absent = new stdClass();
$policy = get_option('imagine_acces_reglages', $absent);
$plans = get_option('imagine_acces_plans');
$canary = 0;
try {
    wp_set_current_user($f['users']['actif']);
    $checks['actif_natif'] = Paywall::decisionPdf($issue)['complet'];
    $checks['article_C08_actif_inchange'] = Paywall::decision(get_post($f['article']))['complet'];
    // Horloge de requête injectée, pas une modification des dates ni des droits natifs.
    $clock = new ReflectionProperty(Paywall::class, 'requestInstant');
    $shared = $clock->getValue();
    try {
        $clock->setValue(null, new DateTimeImmutable('1900-01-01 00:00:00', new DateTimeZone('UTC')));
        Paywall::invalidate();
        $checks['instant_article_PDF_unique'] = !Paywall::decision(get_post($f['article']))['complet']
            && !Paywall::decisionPdf($issue)['complet'];
    } finally {
        $clock->setValue(null, $shared);
        Paywall::invalidate();
    }
    wp_set_current_user(0);
    $checks['article_C08_anonyme_inchange'] = !Paywall::decision(get_post($f['article']))['complet'];
    wp_set_current_user($f['users']['actif']);
    foreach (['offert', 'groupe'] as $type) {
        update_option('imagine_acces_plans', array_replace($plans, [$f['plan'] => $type]));
        $decision = Paywall::decisionPdf($issue);
        $checks[$type . '_natif_meme_droit'] = $decision['complet'] && $decision['motif'] === $type . '_actif';
    }
    update_option('imagine_acces_plans', $plans);
    $canary = wp_insert_post(['post_type' => 'imagine_numero', 'post_status' => 'draft',
        'post_title' => 'Canari éphémère entièrement fictif C11',
        'meta_input' => ['_imagine_c11_fixture' => 'politique', 'imagine_sortie' => '2025-12-01']]);
    // Publication seulement sur l'objet de décision, aucun contenu public temporaire.
    $old = get_post($canary); $old->post_status = 'publish';
    foreach (['ferme' => false, 'ouvert' => true] as $value => $expected) {
        update_option('imagine_acces_reglages', ['contenu_futur' => 'ferme_tous',
            'pdf_robot' => 'extrait', 'pdf_anterieur_abonnement' => $value]);
        $checks['C10_pdf_anterieur_' . $value] = Paywall::decisionPdf($old)['complet'] === $expected;
    }
    $now = new DateTimeImmutable(gmdate('Y-m-d H:i:s'), new DateTimeZone('UTC'));
    $robot = new \Imagine\Pilotage\Robots\Decision(\Imagine\Pilotage\Robots\Motif::VerifieDns, 'google');
    $content = ['reserve' => true, 'numero' => (string) $issue->ID, 'type' => 'pdf',
        'sortie' => $now->modify('-1 day'), 'decouverte' => false];
    foreach (['extrait' => false, 'complet' => true] as $value => $expected) {
        update_option('imagine_acces_reglages', ['contenu_futur' => 'ferme_tous',
            'pdf_robot' => $value, 'pdf_anterieur_abonnement' => 'ferme']);
        // Contrat C10/C06 sur une entrée robot synthétique, pas une revendication DNS Internet.
        $checks['C10_pdf_robot_' . $value] = Paywall::deciderContenu($content,
            ['identifie' => false, 'droits' => []], $robot, $now)->complet === $expected;
    }
    wp_set_current_user($f['users']['sans-droit']);
    $checks['sans_droit_ferme'] = !Paywall::decisionPdf($issue)['complet'];
    $c09 = get_option('imagine_c09_fixture');
    foreach (['P-NUMERO', 'V-DEC', 'P-COOP', 'A-SUSP', 'A-EXPIRE', 'A-VIR'] as $profile) {
        wp_set_current_user($c09['users'][$profile]);
        $checks[$profile . '_ferme'] = !Paywall::decisionPdf($issue)['complet'];
    }
    wp_set_current_user($f['users']['actif']);
    foreach (['invalide', '2099-01-01'] as $date) {
        update_post_meta($canary, 'imagine_sortie', $date);
        $checks['date_' . $date . '_fermee'] = !Paywall::decisionPdf($old)['complet'];
    }
    $filter = static function ($value, $id, $key) use ($f) {
        if ($id === $f['memberships']['actif'] && $key === '_subscription_id') {
            throw new RuntimeException('Panne native C11 synthétique.');
        }
        return $value;
    };
    add_filter('get_post_metadata', $filter, 10, 3);
    try {
        $checks['erreur_native_fermee_apres_positif'] = !Paywall::decisionPdf($issue)['complet'];
    } finally {
        remove_filter('get_post_metadata', $filter, 10);
    }
    $checks['positif_retabli'] = Paywall::decisionPdf($issue)['complet'];
    $path = PdfNumero::path($issue->ID);
    $checks['stockage_hors_docroot'] = !str_starts_with(realpath($path), realpath(ABSPATH) . '/')
        && (fileperms($path) & 0777) === 0600;
    $documentRoot = $_SERVER['DOCUMENT_ROOT'] ?? null;
    try {
        // WordPress installé dans un sous-répertoire public : ABSPATH seul ne suffit pas.
        $_SERVER['DOCUMENT_ROOT'] = dirname(rtrim(ABSPATH, '/'));
        try {
            PdfNumero::path($issue->ID);
            $checks['racine_publique_parent_refusee'] = false;
        } catch (Throwable) {
            $checks['racine_publique_parent_refusee'] = true;
        }
    } finally {
        if ($documentRoot === null) {
            unset($_SERVER['DOCUMENT_ROOT']);
        } else {
            $_SERVER['DOCUMENT_ROOT'] = $documentRoot;
        }
    }
} finally {
    if ($policy === $absent) {
        delete_option('imagine_acces_reglages');
    } else {
        update_option('imagine_acces_reglages', $policy);
    }
    update_option('imagine_acces_plans', $plans);
    if ($canary && get_post_meta($canary, '_imagine_c11_fixture', true) === 'politique') {
        wp_delete_post($canary, true);
    }
    wp_set_current_user($user);
}
$checks['restauration_exacte_options'] = get_option('imagine_acces_plans') === $plans
    && ($policy === $absent ? get_option('imagine_acces_reglages', $absent) === $absent
        : get_option('imagine_acces_reglages') === $policy);
$checks['canari_supprime'] = !$canary || !get_post($canary);
echo wp_json_encode($checks);
if (in_array(false, $checks, true)) {
    WP_CLI::halt(1);
}
