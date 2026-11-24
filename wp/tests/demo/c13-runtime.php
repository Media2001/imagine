<?php
/** C13 : premier tracer — calendrier et permissions réels. */
declare(strict_types=1);
namespace Imagine\Demo\C13Tests;
$checks = [];
$checks['raccord_present'] = class_exists(\Imagine\Site\EnvoiNatif::class)
    && class_exists(\Imagine\Site\ListeEnvoiAdmin::class);
if ($checks['raccord_present']) {
    $checks['calendrier_15_clotures'] = count(\Imagine\Site\EnvoiNatif::calendrier()->numeros) === 15;
    $fixture = get_option('imagine_c09_fixture');
    foreach (['E-ABO' => true, 'E-ADMIN' => true, 'E-REDAC' => false, 'A-CARTE' => false] as $profile => $allowed) {
        wp_set_current_user($fixture['users'][$profile]);
        $checks['capacite_' . $profile] = \Imagine\Site\ListeEnvoiAdmin::autorise() === $allowed;
    }
    wp_set_current_user(0);
    $checks['anonyme_ferme'] = !\Imagine\Site\ListeEnvoiAdmin::autorise();
}
echo wp_json_encode($checks);
