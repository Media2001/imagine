<?php
/** Règle pure, sans WordPress : le moteur C06 reste inchangé. */
declare(strict_types=1);
require __DIR__ . '/../../plugins/imagine-site/AchatNumero.php';
use Imagine\Site\AchatNumero;
$base = ['client' => 42, 'etat' => 'processing', 'payee' => true,
    'acquis' => new DateTimeImmutable('2020-01-01 00:00:00', new DateTimeZone('UTC')),
    'remboursement' => false, 'numero' => 12, 'instantane' => 12, 'publie' => true, 'quantite' => 1];
$checks = [];
$checks['payee_processing'] = AchatNumero::droit(42, $base)['numero'] === '12';
$checks['payee_completed'] = AchatNumero::droit(42, array_replace($base, ['etat' => 'completed'])) !== null;
foreach (['pending', 'on-hold', 'failed', 'cancelled', 'refunded', 'trash', 'checkout-draft', 'custom-paid'] as $status) {
    $checks[$status . '_fermee'] = AchatNumero::droit(42, array_replace($base, ['etat' => $status])) === null;
}
foreach (['client' => 43, 'payee' => false, 'acquis' => null, 'remboursement' => true,
    'instantane' => 0, 'publie' => false, 'quantite' => 0] as $field => $value) {
    $checks[$field . '_invalide_ferme'] = AchatNumero::droit(42, array_replace($base, [$field => $value])) === null;
}
$checks['invite_ferme'] = AchatNumero::droit(0, array_replace($base, ['client' => 0])) === null;
foreach ([13, 0, null] as $mapping) {
    $checks['catalogue_' . var_export($mapping, true) . '_ne_deplace_pas_acquisition'] = AchatNumero::droit(42, array_replace($base, ['numero' => $mapping]))['numero'] === '12';
}
$checks['publication_absente_fermee'] = AchatNumero::droit(42, array_diff_key($base, ['publie' => true])) === null;
$checks['date_native_conservee_sans_expiration'] = AchatNumero::droit(42, $base)['acquis_le'] === $base['acquis'];
$checks['contrat_moteur_exact'] = array_keys(AchatNumero::droit(42, $base)) === ['type', 'numero', 'acquis_le'];
echo json_encode($checks, JSON_THROW_ON_ERROR) . "\n";
exit(in_array(false, $checks, true) ? 1 : 0);
