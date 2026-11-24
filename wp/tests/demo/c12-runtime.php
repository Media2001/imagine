<?php
/** C12 : une ouverture persistée, sans toucher aux bibliothèques closes. */
declare(strict_types=1);
use Imagine\Site\Decouverte;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085') { throw new RuntimeException('Cible C12 refusée.'); }
$checks = ['raccord_disponible' => class_exists(Decouverte::class)];
if ($checks['raccord_disponible']) {
    $id = get_option('imagine_c09_fixture')['users']['V-DEC'];
    if (get_user_meta($id, '_imagine_c09_fixture', true) !== 'V-DEC') { throw new RuntimeException('Propriétaire refusé.'); }
    $key = Decouverte::key($id);
    $absent = new stdClass();
    $before = get_option($key, $absent);
    $verified = get_user_meta($id, 'imagine_email_confirme', true);
    $policy = get_option(Decouverte::OPTION, $absent);
    $relecture = get_option(Decouverte::RELECTURE, $absent);
    $now = new DateTimeImmutable('2026-11-24 10:00:00', new DateTimeZone('UTC'));
    try {
        delete_option($key);
        update_option(Decouverte::RELECTURE, 'fermee');
        update_user_meta($id, 'imagine_email_confirme', '1');
        $settings = ['ouverture' => 'fermee', 'forme' => 'articles', 'jours' => 7, 'nombre' => 2,
            'numeros' => array_map(static fn ($slug): string => (string) get_option('imagine_demo_manifest')[$slug],
                ['demo-2026-t4', 'demo-2026-t3', 'demo-2026-t2'])];
        update_option(Decouverte::OPTION, $settings);
        $checks['defaut_ferme'] = Decouverte::ouvrir($id, $now) === null;
        $settings['ouverture'] = 'premiere_lecture'; update_option(Decouverte::OPTION, $settings);
        delete_user_meta($id, 'imagine_email_confirme');
        $checks['email_non_confirme_ferme'] = Decouverte::ouvrir($id, $now) === null;
        update_user_meta($id, 'imagine_email_confirme', '1');
        $firstName = get_user_meta($id, 'first_name', true);
        try {
            update_user_meta($id, 'first_name', '');
            $checks['identite_incomplete_fermee'] = Decouverte::ouvrir($id, $now) === null;
        } finally { update_user_meta($id, 'first_name', $firstName); }
        $first = Decouverte::ouvrir($id, $now);
        $checks['ouverture_compte_verifie'] = is_array($first) && $first['debut'] === $now->format('Y-m-d H:i:s') && $first['articles'] === [];
        $checks['jamais_renouveler'] = Decouverte::ouvrir($id, $now->modify('+30 days')) === $first;
        $checks['decompte_raccorde'] = method_exists(Decouverte::class, 'decider');
        if ($checks['decompte_raccorde']) {
            $originalUser = get_current_user_id();
            wp_set_current_user($id);
            $robot = new \Imagine\Pilotage\Robots\Decision(\Imagine\Pilotage\Robots\Motif::AgentInconnu);
            $visitor = ['identifie' => true, 'droits' => []];
            $content = ['reserve' => true, 'numero' => $settings['numeros'][0], 'type' => 'article',
                'sortie' => $now->modify('-1 day'), 'decouverte' => true];
            delete_option($key);
            $future = $content; $future['sortie'] = $now->modify('+1 day');
            $futureDecision = Decouverte::decider($future, $visitor, $robot, $now, 912004);
            $checks['futur_sans_etat_motif_sans_ouverture'] = !$futureDecision->complet
                && $futureDecision->motif->value === 'contenu_futur_ferme_par_reglage' && Decouverte::etat($id) === null;
            $notDesignated = $content; $notDesignated['decouverte'] = false;
            $checks['non_designe_sans_ouverture'] = !Decouverte::decider($notDesignated, $visitor, $robot, $now, 912005)->complet
                && Decouverte::etat($id) === null;
            $checks['premier_article'] = Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet
                && Decouverte::etat($id)['articles'] === [912001];
            $availableState = Decouverte::etat($id);
            $futureDecision = Decouverte::decider($future, $visitor, $robot, $now, 912004);
            $checks['futur_pas_de_credit'] = !$futureDecision->complet
                && $futureDecision->motif->value === 'contenu_futur_ferme_par_reglage'
                && Decouverte::etat($id) === $availableState;
            $checks['non_designe_meme_numero_sans_credit'] = !Decouverte::decider($notDesignated, $visitor, $robot, $now, 912005)->complet
                && Decouverte::etat($id) === $availableState;
            $checks['relecture_idempotente'] = Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet
                && Decouverte::etat($id)['articles'] === [912001];
            $second = $content; $second['numero'] = $settings['numeros'][1];
            $third = $content; $third['numero'] = $settings['numeros'][2];
            $checks['dernier_credit_livre'] = Decouverte::decider($second, $visitor, $robot, $now, 912002)->complet;
            $exhausted = Decouverte::decider($third, $visitor, $robot, $now, 912003);
            $checks['epuisement_moteur_bloc'] = !$exhausted->complet && $exhausted->motif->value === 'decouverte_epuisee'
                && $exhausted->bloc->value === 'decouverte_epuisee' && Decouverte::etat($id)['articles'] === [912001, 912002];
            $checks['relecture_apres_quota_fermee_sans_credit'] = !Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet
                && Decouverte::etat($id)['articles'] === [912001, 912002];
            update_option(Decouverte::RELECTURE, 'rester_lisible');
            $checks['relecture_apres_quota_lisible_sans_recredit'] = Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet
                && Decouverte::decider($second, $visitor, $robot, $now, 912002)->complet
                && !Decouverte::decider($third, $visitor, $robot, $now, 912003)->complet
                && Decouverte::etat($id)['articles'] === [912001, 912002];
            update_option(Decouverte::RELECTURE, 'fermee');
            $pdf = $content; $pdf['type'] = 'pdf';
            $checks['pdf_hors_decouverte'] = !Decouverte::decider($pdf, $visitor, $robot, $now, 912004)->complet;
            $settings['nombre'] = 3; update_option(Decouverte::OPTION, $settings);
            $checks['reglage_change_sans_recredit'] = !Decouverte::decider($content, $visitor, $robot, $now, 912003)->complet
                && Decouverte::etat($id)['reglages']['nombre'] === 2;
            delete_option($key); $settings['forme'] = 'duree'; $settings['jours'] = 1;
            update_option(Decouverte::OPTION, $settings); Decouverte::ouvrir($id, $now);
            $checks['duree_avant_limite'] = Decouverte::decider($content, $visitor, $robot, $now->modify('+86399 seconds'), 912001)->complet;
            $boundary = Decouverte::decider($content, $visitor, $robot, $now->modify('+86400 seconds'), 912002);
            $checks['duree_fin_exclue_moteur'] = !$boundary->complet && $boundary->motif->value === 'decouverte_epuisee';
            $scope = $content; $scope['numero'] = '999999';
            $checks['hors_perimetre_pas_de_credit'] = !Decouverte::decider($scope, $visitor, $robot, $now, 912003)->complet
                && Decouverte::etat($id)['articles'] === [912001];
            update_option($key, 'corrompu');
            $checks['etat_invalide_jamais_recree'] = !Decouverte::decider($content, $visitor, $robot, $now, 912003)->complet
                && get_option($key) === 'corrompu';
            delete_option($key);
            $robotVerified = new \Imagine\Pilotage\Robots\Decision(\Imagine\Pilotage\Robots\Motif::VerifieDns, 'google');
            $checks['robot_verifie_contrat_sans_compteur'] = Decouverte::decider($content, $visitor, $robotVerified, $now, 912003)->complet
                && get_option($key, null) === null;
            Decouverte::ouvrir($id, $now);
            $stopCas = static function (string $query): string {
                global $wpdb;
                return str_starts_with($query, "UPDATE {$wpdb->options} SET option_value =") && str_contains($query, 'imagine_decouverte_compte_')
                    ? "UPDATE {$wpdb->options} SET option_value = option_value WHERE 1=0" : $query;
            };
            add_filter('query', $stopCas);
            try {
                $checks['persistance_refusee_lecture_fermee'] = !Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet
                    && Decouverte::etat($id)['articles'] === [];
            } finally { remove_filter('query', $stopCas); }
            $checks['persistance_retablie_positive'] = Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet;
        }
        if (!function_exists('add_settings_error')) { require_once ABSPATH . 'wp-admin/includes/template.php'; }
        $checks['relecture_deux_valeurs_et_invalide'] = \Imagine\Site\DecouverteReglages::nettoyerRelecture('fermee') === 'fermee'
            && \Imagine\Site\DecouverteReglages::nettoyerRelecture('rester_lisible') === 'rester_lisible'
            && \Imagine\Site\DecouverteReglages::nettoyerRelecture('invalide') === 'fermee';
        $validPolicy = get_option(Decouverte::OPTION);
        $failAudit = static function (string $query): string {
            return str_starts_with($query, 'INSERT INTO') && str_contains($query, 'imagine_reglages_journal_')
                ? 'INSERT INTO imagine_c12_table_inexistante (a) VALUES (1)' : $query;
        };
        global $wpdb; $suppress = $wpdb->suppress_errors(true);
        add_filter('query', $failAudit);
        try {
            $changed = $validPolicy; $changed['jours'] = 13;
            update_option(Decouverte::OPTION, $changed);
            $checks['audit_panne_annule_modification'] = get_option(Decouverte::OPTION) === $validPolicy;
            delete_option(Decouverte::OPTION); add_option(Decouverte::OPTION, $changed, '', false);
            $checks['audit_panne_annule_creation'] = get_option(Decouverte::OPTION, null) === null;
            update_option(Decouverte::RELECTURE, 'rester_lisible');
            $checks['audit_relecture_panne_annule_modification'] = get_option(Decouverte::RELECTURE) === 'fermee';
            delete_option(Decouverte::RELECTURE); add_option(Decouverte::RELECTURE, 'rester_lisible', '', false);
            $checks['audit_relecture_panne_annule_creation'] = get_option(Decouverte::RELECTURE, null) === null;
        } finally {
            remove_filter('query', $failAudit); $wpdb->suppress_errors($suppress);
            update_option(Decouverte::OPTION, $validPolicy);
        }
    } finally {
        if (isset($originalUser)) { wp_set_current_user($originalUser); }
        if ($before === $absent) { delete_option($key); } else { update_option($key, $before); }
        if ($policy === $absent) { delete_option(Decouverte::OPTION); } else { update_option(Decouverte::OPTION, $policy); }
        if ($relecture === $absent) { delete_option(Decouverte::RELECTURE); } else { update_option(Decouverte::RELECTURE, $relecture); }
        if ($verified === '') { delete_user_meta($id, 'imagine_email_confirme'); } else { update_user_meta($id, 'imagine_email_confirme', $verified); }
    }
    $checks['restauration_etat'] = get_option($key, $absent) === $before && get_option(Decouverte::OPTION, $absent) === $policy
        && get_option(Decouverte::RELECTURE, $absent) === $relecture;
}
echo wp_json_encode($checks);
if (in_array(false, $checks, true)) { WP_CLI::halt(1); }
