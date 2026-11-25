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
    test('filtres_paiements_presents', method_exists(EcheancesRegles::class, 'paiements'));
    if (method_exists(EcheancesRegles::class, 'paiements')) {
        $orders = [
            ['id' => 10, 'etat' => 'on-hold', 'paye' => false, 'date_payee' => 0, 'methode' => 'bacs', 'creation' => 10],
            ['id' => 11, 'etat' => 'pending', 'paye' => false, 'date_payee' => 0, 'methode' => 'stripe', 'creation' => 9],
            ['id' => 12, 'etat' => 'failed', 'paye' => false, 'date_payee' => 0, 'methode' => 'bacs', 'creation' => 8],
            ['id' => 13, 'etat' => 'completed', 'paye' => true, 'date_payee' => 1, 'methode' => 'bacs', 'creation' => 7],
            ['id' => 14, 'etat' => 'on-hold', 'paye' => false, 'date_payee' => 1, 'methode' => 'bacs', 'creation' => 6],
            ['id' => 15, 'etat' => 'cancelled', 'paye' => false, 'date_payee' => 0, 'methode' => 'bacs', 'creation' => 5],
            ['id' => 16, 'etat' => 'refunded', 'paye' => false, 'date_payee' => 0, 'methode' => 'bacs', 'creation' => 4],
            ['id' => 17, 'etat' => 'pending', 'paye' => false, 'date_payee' => 0, 'methode' => '', 'creation' => 3],
        ];
        test('attente_statuts_natifs_non_payes', array_column(EcheancesRegles::paiements($orders, 'attente'), 'id') === [17, 11, 10]);
        test('virements_bacs_seulement', array_column(EcheancesRegles::paiements($orders, 'virements'), 'id') === [10]);
        test('echecs_statut_natif_sans_inventer_delai', array_column(EcheancesRegles::paiements($orders, 'echecs'), 'id') === [12]);
        $bad = false; try { EcheancesRegles::paiements([], 'autre'); } catch (InvalidArgumentException) { $bad = true; }
        test('vue_invalide_refusee', $bad);
    }
    test('mandats_export_presents', method_exists(EcheancesRegles::class, 'mandats') && method_exists(EcheancesRegles::class, 'csv'));
    if (method_exists(EcheancesRegles::class, 'mandats') && method_exists(EcheancesRegles::class, 'csv')) {
        $paper = array_map(static fn ($r) => $r + ['methode' => 'imagine_papier', 'reference' => 'FICTIF', 'abonne' => 'Fictif', 'montant' => '60.00', 'devise' => 'EUR'], $rows);
        test('mandats_renouvellement_actif_uniquement', array_column(EcheancesRegles::mandats($paper, $now, 30), 'id') === [1]);
        $paper[0]['methode'] = 'bacs';
        test('aucun_bacs_dans_mandats', EcheancesRegles::mandats($paper, $now, 30) === []);
        $overdue = array_replace($paper[0], ['id' => 20, 'methode' => 'imagine_papier', 'prochaine' => $now - 1, 'fin' => $now + 86400]);
        test('mandat_date_native_passee_reste_a_lancer', array_column(EcheancesRegles::mandats([$overdue], $now, 30), 'id') === [20]);
        $stream = fopen('php://memory', 'w+');
        EcheancesRegles::csv($stream, [['abonne' => " \t=FORMULE", 'montant' => '60.00', 'devise' => 'EUR', 'reference' => '+FICTIF', 'echeance' => $now, 'iban' => 'INTERDIT']]);
        rewind($stream); $csv = stream_get_contents($stream); rewind($stream); $header = fgetcsv($stream, 0, ';', '"', ''); $line = fgetcsv($stream, 0, ';', '"', ''); fclose($stream);
        test('CSV_colonnes_strictes_sans_IBAN', $header === ['Abonné', 'Montant', 'Devise', 'Référence du mandat', 'Échéance (UTC)'] && !str_contains($csv, 'INTERDIT'));
        test('CSV_formules_neutralisees', $line[0] === "' \t=FORMULE" && $line[3] === "'+FICTIF");
        test('CSV_date_native_UTC', $line[4] === '2026-11-25 12:00:00');
    }
    foreach ([30, 90, 180] as $days) {
        $bound = $now + $days * 86400;
        $base = ['etat' => 'active', 'fin' => 0, 'methode' => 'imagine_papier', 'reference' => 'FICTIF'];
        $edge = [$base + ['id' => 9, 'prochaine' => $bound], $base + ['id' => 7, 'prochaine' => $bound + 1],
            $base + ['id' => 3, 'prochaine' => $bound], $base + ['id' => 8, 'prochaine' => $bound - 1],
            $base + ['id' => 2, 'prochaine' => 0]];
        test('borne_' . $days . '_exacte_voisines_1s_tri_ID_sans_dates', array_column(EcheancesRegles::echeances($edge, $now, $days), 'id') === [8, 3, 9]);
        test('mandats_borne_' . $days . '_exacte_voisines_1s_tri_ID_sans_dates', array_column(EcheancesRegles::mandats($edge, $now, $days), 'id') === [8, 3, 9]);
    }
    $base = ['id' => 90, 'etat' => 'on-hold', 'methode' => 'imagine_papier', 'reference' => '',
        'prochaine' => $now + 1, 'fin' => 0, 'montant' => '99.00', 'devise' => 'EUR'];
    $due = ['id' => 91, 'etat' => 'failed', 'paye' => false, 'date_payee' => 0,
        'creation' => $now - 1, 'montant' => '12.34', 'devise' => 'EUR'];
    $list = EcheancesRegles::mandats([$base + ['renouvellements' => [$due, $due]]], $now, 30);
    test('mandat_onhold_renouvellement_du_sans_doublon_futur', count($list) === 1 && $list[0]['id'] === 91
        && $list[0]['montant'] === '12.34' && $list[0]['echeance'] === $now - 1);
    test('mandat_reference_manquante_visible', ($list[0]['reference'] ?? '') === 'Référence manquante');
    test('onhold_sans_dette_non_autorise_en_bloc', EcheancesRegles::mandats([$base], $now, 30) === []);
    $due['paye'] = true;
    test('renouvellement_paye_non_represente_comme_du', EcheancesRegles::mandats([$base + ['renouvellements' => [$due]]], $now, 30) === []);
}
$failures = array_keys(array_filter($checks, static fn ($v) => !$v));
echo json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures], JSON_PRETTY_PRINT) . "\n";
exit($failures ? 1 : 0);
