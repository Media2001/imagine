<?php
/** C15 pure rules, deliberately no WordPress bootstrap. */
declare(strict_types=1);
use Imagine\Site\EcheancesRegles;
$checks = [];
function test(string $name, bool $ok): void { global $checks; $checks[$name] = $ok; }
$path = __DIR__ . '/../../plugins/imagine-site/EcheancesRegles.php';
if (is_file($path)) { require_once $path; }
test('regles_presentes', class_exists(EcheancesRegles::class));
if (class_exists(EcheancesRegles::class)) {
    $now = strtotime('2026-11-25 12:00:00 UTC');
    $rows = [
        ['id' => 1, 'etat' => 'active', 'prochaine' => $now + 29 * 86400, 'fin' => $now + 30 * 86400],
        ['id' => 2, 'etat' => 'pending-cancel', 'prochaine' => 0, 'fin' => $now + 90 * 86400],
        ['id' => 3, 'etat' => 'expired', 'prochaine' => 0, 'fin' => $now - 1],
        ['id' => 4, 'etat' => 'cancelled', 'prochaine' => $now + 1, 'fin' => $now + 1],
        ['id' => 5, 'etat' => 'active', 'prochaine' => $now + 181 * 86400, 'fin' => 0],
        ['id' => 6, 'etat' => 'on-hold', 'prochaine' => $now, 'fin' => 0],
    ];
    test('30_jours_inclus_tri_date_id', array_column(EcheancesRegles::echeances($rows, $now, 30), 'id') === [6, 1]);
    test('90_jours_borne_incluse', array_column(EcheancesRegles::echeances($rows, $now, 90), 'id') === [6, 1, 2]);
    test('180_jours_sans_expire_annule', array_column(EcheancesRegles::echeances($rows, $now, 180), 'id') === [6, 1, 2]);
    test('date_plus_proche', EcheancesRegles::echeances([$rows[0]], $now, 30)[0]['echeance'] === $rows[0]['prochaine']);
    $bad = false; try { EcheancesRegles::echeances([], $now, 31); } catch (InvalidArgumentException) { $bad = true; }
    test('periode_invalide_refusee', $bad);
}
$failures = array_keys(array_filter($checks, static fn ($v) => !$v));
echo json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures], JSON_PRETTY_PRINT) . "\n";
exit($failures ? 1 : 0);
