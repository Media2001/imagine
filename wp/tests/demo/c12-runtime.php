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
    $now = new DateTimeImmutable('2026-11-24 10:00:00', new DateTimeZone('UTC'));
    try {
        delete_option($key);
        update_user_meta($id, 'imagine_email_confirme', '1');
        $settings = ['ouverture' => 'fermee', 'forme' => 'articles', 'jours' => 7, 'nombre' => 2,
            'numeros' => [(string) get_option('imagine_demo_manifest')['demo-2026-t4']]];
        update_option(Decouverte::OPTION, $settings);
        $checks['defaut_ferme'] = Decouverte::ouvrir($id, $now) === null;
        $settings['ouverture'] = 'premiere_lecture'; update_option(Decouverte::OPTION, $settings);
        delete_user_meta($id, 'imagine_email_confirme');
        $checks['email_non_confirme_ferme'] = Decouverte::ouvrir($id, $now) === null;
        update_user_meta($id, 'imagine_email_confirme', '1');
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
            $checks['premier_article'] = Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet
                && Decouverte::etat($id)['articles'] === [912001];
            $checks['relecture_idempotente'] = Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet
                && Decouverte::etat($id)['articles'] === [912001];
            $checks['dernier_credit_livre'] = Decouverte::decider($content, $visitor, $robot, $now, 912002)->complet;
            $exhausted = Decouverte::decider($content, $visitor, $robot, $now, 912003);
            $checks['epuisement_moteur_bloc'] = !$exhausted->complet && $exhausted->motif->value === 'decouverte_epuisee'
                && $exhausted->bloc->value === 'decouverte_epuisee' && Decouverte::etat($id)['articles'] === [912001, 912002];
            $checks['relecture_apres_quota_sans_credit'] = Decouverte::decider($content, $visitor, $robot, $now, 912001)->complet
                && Decouverte::etat($id)['articles'] === [912001, 912002];
            $future = $content; $future['sortie'] = $now->modify('+1 day');
            $checks['futur_pas_de_credit'] = !Decouverte::decider($future, $visitor, $robot, $now, 912004)->complet;
            $pdf = $content; $pdf['type'] = 'pdf';
            $checks['pdf_hors_decouverte'] = !Decouverte::decider($pdf, $visitor, $robot, $now, 912004)->complet;
        }
    } finally {
        if (isset($originalUser)) { wp_set_current_user($originalUser); }
        if ($before === $absent) { delete_option($key); } else { update_option($key, $before); }
        if ($policy === $absent) { delete_option(Decouverte::OPTION); } else { update_option(Decouverte::OPTION, $policy); }
        if ($verified === '') { delete_user_meta($id, 'imagine_email_confirme'); } else { update_user_meta($id, 'imagine_email_confirme', $verified); }
    }
    $checks['restauration_etat'] = get_option($key, $absent) === $before && get_option(Decouverte::OPTION, $absent) === $policy;
}
echo wp_json_encode($checks);
if (in_array(false, $checks, true)) { WP_CLI::halt(1); }
