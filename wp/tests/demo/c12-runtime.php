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
    } finally {
        if ($before === $absent) { delete_option($key); } else { update_option($key, $before); }
        if ($policy === $absent) { delete_option(Decouverte::OPTION); } else { update_option(Decouverte::OPTION, $policy); }
        if ($verified === '') { delete_user_meta($id, 'imagine_email_confirme'); } else { update_user_meta($id, 'imagine_email_confirme', $verified); }
    }
    $checks['restauration_etat'] = get_option($key, $absent) === $before && get_option(Decouverte::OPTION, $absent) === $policy;
}
echo wp_json_encode($checks);
if (in_array(false, $checks, true)) { WP_CLI::halt(1); }
