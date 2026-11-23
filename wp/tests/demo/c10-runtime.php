<?php
/** C10 : tranche réelle d'enregistrement et rendu natifs, sur le site fictif seul. */
declare(strict_types=1);
namespace Imagine\Demo\C10Tests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C10 requise.');
}
$checks = ['ecran_present' => class_exists('Imagine\\Pilotage\\Administration\\Reglages')];
if ($checks['ecran_present']) {
    $screen = new \Imagine\Pilotage\Administration\Reglages();
    $screen->enregistrer();
    $registered = get_registered_settings();
    $checks['trois_options_meme_groupe'] = count(array_filter($screen->options(), static fn ($name) =>
        isset($registered[$name]) && $registered[$name]['group'] === 'imagine_reglages'
        && $registered[$name]['show_in_rest'] === false)) === 3;
    wp_set_current_user(get_user_by('login', 'e-admin')->ID);
    ob_start();
    $screen->page();
    $html = ob_get_clean();
    foreach (['Accès', 'Paiement en quatre fois', 'Liste d’envoi', 'À confirmer par Imagine',
        'Défaut', 'Journal des modifications', 'options.php', '_wpnonce'] as $text) {
        $checks['rendu_' . $text] = str_contains($html, $text);
    }
    $checks['huit_champs'] = substr_count($html, 'class="imagine-reglage"') === 8;
    $checks['cap_admin'] = apply_filters('option_page_capability_imagine_reglages', 'manage_options') === 'manage_options';
    wp_set_current_user(get_user_by('login', 'e-redac')->ID);
    $checks['redacteur_sans_droit'] = !current_user_can('manage_options');
    wp_set_current_user(0);
}
// Corrections arbitrées : vrais hooks/options ; restauration exacte en finally.
if ($checks['ecran_present']) {
    $option = 'imagine_acces_reglages';
    $original = get_option($option, $screen->defauts()[$option]);
    $userBefore = get_current_user_id();
    try {
        wp_set_current_user(get_user_by('login', 'e-admin')->ID);
        $fixture = get_option('imagine_c08_fixture');
        $post = get_post($fixture['article']);
        $issue = (int) get_post_meta($post->ID, 'imagine_numero_id', true);
        $dateBefore = get_post_meta($issue, 'imagine_sortie', true);
        try {
            update_post_meta($issue, 'imagine_sortie', '2099-01-01');
            update_option($option, array_replace($original, ['contenu_futur' => 'ferme_tous']));
            $checks['futur_ferme'] = !\Imagine\Site\Paywall::decision($post)['complet'];
            update_option($option, array_replace($original, ['contenu_futur' => 'equipe']));
            $checks['futur_equipe_reglage_effectif'] = \Imagine\Site\Paywall::decision($post)['complet'];
        } finally {
            update_post_meta($issue, 'imagine_sortie', $dateBefore);
        }
        wp_set_current_user(get_option('imagine_c09_fixture')['users']['A-VIR']);
        $checks['A_VIR_virement_non_valide'] = \Imagine\Site\Paywall::decision($post)['motif'] === 'virement_non_valide';
        // Rôle futur C09 reconnu sans modifier le compte ni la définition native persistée.
        $teamUser = get_option('imagine_c09_fixture')['users']['E-ABO'];
        $roles = wp_roles();
        $role = 'imagine_referent_abonnements';
        $hadRole = isset($roles->role_objects[$role]);
        $oldRole = $roles->role_objects[$role] ?? null;
        $roles->role_objects[$role] = new \WP_Role($role, ['read' => true]);
        $capabilities = static function ($value, $id, $key) use ($teamUser, $role) {
            global $wpdb;
            return $id === $teamUser && $key === $wpdb->get_blog_prefix() . 'capabilities'
                ? [[$role => true]] : $value;
        };
        add_filter('get_user_metadata', $capabilities, 10, 3);
        try {
            wp_set_current_user($teamUser);
            $checks['role_referent_lecture_equipe'] = \Imagine\Site\Paywall::decision($post)['motif'] === 'equipe';
        } finally {
            remove_filter('get_user_metadata', $capabilities, 10);
            if ($hadRole) {
                $roles->role_objects[$role] = $oldRole;
            } else {
                unset($roles->role_objects[$role]);
            }
        }
        wp_set_current_user(get_user_by('login', 'e-admin')->ID);
        $checks['pdf_policies_connected'] = method_exists(\Imagine\Site\Paywall::class, 'deciderContenu');
        if ($checks['pdf_policies_connected']) {
            $now = new \DateTimeImmutable('2026-11-23 12:00:00 UTC');
            $content = ['reserve' => true, 'numero' => 'C10-PDF', 'type' => 'pdf',
                'sortie' => $now->modify('-1 year'), 'decouverte' => false];
            $visitor = ['identifie' => false, 'droits' => []];
            // Entrée robot explicitement synthétique : aucun DNS ni robot réel revendiqué.
            $robot = new \Imagine\Pilotage\Robots\Decision(\Imagine\Pilotage\Robots\Motif::VerifieDns, 'google');
            foreach (['extrait' => false, 'complet' => true] as $value => $expected) {
                update_option($option, array_replace($original, ['pdf_robot' => $value]));
                $checks['pdf_robot_' . $value] = \Imagine\Site\Paywall::deciderContenu($content, $visitor, $robot, $now)->complet === $expected;
            }
            $visitor = ['identifie' => true, 'droits' => [['type' => 'abonnement', 'etat' => 'actif',
                'debut' => $now->modify('-1 month'), 'fin' => $now->modify('+1 month')]]];
            $robot = new \Imagine\Pilotage\Robots\Decision(\Imagine\Pilotage\Robots\Motif::AgentInconnu);
            foreach (['ferme' => false, 'ouvert' => true] as $value => $expected) {
                update_option($option, array_replace($original, ['pdf_anterieur_abonnement' => $value]));
                $checks['pdf_anterieur_' . $value] = \Imagine\Site\Paywall::deciderContenu($content, $visitor, $robot, $now)->complet === $expected;
            }
        }
        update_option($option, $original);
        $journalBefore = $screen->journal();
        $blockJournal = static function ($sql) {
            return str_starts_with(ltrim($sql), 'INSERT') && str_contains($sql, 'imagine_reglages_journal_')
                ? 'SELECT 1 WHERE 0=1' : $sql;
        };
        add_filter('query', $blockJournal);
        try {
            update_option($option, array_replace($original, ['contenu_futur' => 'equipe']));
        } finally {
            remove_filter('query', $blockJournal);
        }
        $checks['journal_KO_refuse_et_conserve'] = get_option($option) === $original;
        $checks['journal_KO_aucun_evenement'] = $screen->journal() === $journalBefore;
        $checks['journal_KO_previent'] = (bool) array_filter(get_settings_errors($option),
            static fn ($error) => $error['code'] === 'imagine_journal_indisponible');
    } finally {
        update_option($option, $original);
        wp_set_current_user($userBefore);
    }
}
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
if ($failures) { \WP_CLI::halt(1); }
