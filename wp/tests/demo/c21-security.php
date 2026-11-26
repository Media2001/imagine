<?php

declare(strict_types=1);

namespace Imagine\Demo\C21;

use Imagine\Site\Confidentialite;

if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible C21 refusée.');
}
$checks = [];
$f = get_option('imagine_c09_fixture');
$u = get_userdata($f['users']['A-SANSMAIL']);
$source = ['data' => [['data' => [['name' => 'Email Address', 'value' => $u->user_email],
    ['name' => 'Internal Note', 'value' => 'INTERNE'], ['name' => 'Payment Token', 'value' => 'SECRET']]]], 'done' => true];
$result = Confidentialite::filtrerPage($source, 1, $u->user_email, 1, 0, false, 'wordpress-user');
$checks['sans_email_marque_meme_hors_invalid'] = !str_contains(wp_json_encode($result), $u->user_email)
    && str_contains(wp_json_encode($result), '[sans adresse');
$checks['notes_et_jetons_retires'] = count($result['data'][0]['data']) === 1;
$checks['reponse_invalide_preservee_pour_erreur_native'] = Confidentialite::filtrerPage(
    ['erreur' => true], 1, 'inconnu@example.org', 1, 0, false, 'wordpress-user'
) === ['erreur' => true];
$checks['email_non_marque_conserve'] = Confidentialite::filtrerPage(
    ['data' => [['data' => [['name' => 'Email', 'value' => 'normal@example.org']]]]],
    1, 'normal@example.org', 1, 0, false, 'wordpress-user'
)['data'][0]['data'][0]['value'] === 'normal@example.org';
echo wp_json_encode(['checks' => $checks, 'total' => count($checks),
    'failures' => array_keys(array_filter($checks, static fn ($v): bool => !$v))]);
