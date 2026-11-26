<?php

declare(strict_types=1);

use Imagine\Site\CooperateursRegles as R;

$root = '/repo/wp/plugins/imagine-site/';
if (!is_file($root . 'CooperateursRegles.php')) {
    fwrite(STDERR, "FAIL attribut coopérateur absent\n"); exit(1);
}
require $root . 'CooperateursRegles.php';
$checks = [];
foreach ([[], ['subscriber'], ['editor'], ['shop_manager'], ['manage_options']] as $roles) {
    $checks['refus_role_' . implode('_', $roles)] = !R::administration($roles);
}
$checks['admin_seul'] = R::administration(['administrator']);
$state = ['cooperateur' => true, 'source' => 'administration', 'date_utc' => '2026-11-26T15:00:00Z'];
$checks['coop_ouvre'] = R::lecture($state, [], true);
$checks['anonyme_ferme'] = !R::lecture($state, [], false);
$checks['abonne_ferme'] = !R::lecture([], ['subscriber'], true);
$checks['admin_ouvre'] = R::lecture([], ['administrator'], true);
foreach ([null, '1', ['cooperateur' => '1'], array_replace($state, ['source' => 'coophub']), array_replace($state, ['date_utc' => 'hier']), array_replace($state, ['cooperateur' => false])] as $i => $bad) {
    $checks['etat_invalide_' . $i] = !R::lecture($bad, [], true);
}
$bad = array_keys(array_filter($checks, fn ($v) => !$v));
echo json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $bad]);
exit($bad ? 1 : 0);
