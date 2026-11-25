<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\EcheancesRegles;
use PHPUnit\Framework\TestCase;
use PHPUnit\Framework\Attributes\DataProvider;

final class EcheancesReglesTest extends TestCase
{
    public static function periodes(): array
    {
        return ['J30' => [30], 'J90' => [90], 'J180' => [180]];
    }

    #[DataProvider('periodes')]
    public function testBornesExactesVoisinesUneSecondeEtEgalitesId(int $days): void
    {
        $now = 1000000;
        $end = $now + $days * 86400;
        $base = ['etat' => 'active', 'fin' => 0, 'methode' => 'imagine_papier', 'reference' => 'FICTIF'];
        $rows = [
            $base + ['id' => 9, 'prochaine' => $end],
            $base + ['id' => 7, 'prochaine' => $end + 1],
            $base + ['id' => 3, 'prochaine' => $end],
            $base + ['id' => 8, 'prochaine' => $end - 1],
            $base + ['id' => 2, 'prochaine' => 0],
        ];
        self::assertSame([8, 3, 9], array_column(EcheancesRegles::echeances($rows, $now, $days), 'id'));
        self::assertSame([8, 3, 9], array_column(EcheancesRegles::mandats($rows, $now, $days), 'id'));
        // La fin native seule est également inclusive à la borne exacte.
        $rows[0]['prochaine'] = 0;
        $rows[0]['fin'] = $end;
        self::assertSame($end, EcheancesRegles::echeances([$rows[0]], $now, $days)[0]['echeance']);
    }

    public function testEtatsEcheancesEtDateLaPlusProcheSansDateInventee(): void
    {
        $now = 100;
        $rows = [];
        foreach (['active', 'pending-cancel', 'on-hold', 'pending', 'cancelled', 'expired'] as $id => $state) {
            $rows[] = ['id' => $id, 'etat' => $state, 'prochaine' => 102, 'fin' => 101];
        }
        self::assertSame([0, 1, 2, 3], array_column(EcheancesRegles::echeances($rows, $now, 30), 'id'));
        self::assertSame(101, EcheancesRegles::echeances([$rows[0]], $now, 30)[0]['echeance']);
        self::assertSame([], EcheancesRegles::echeances([['id' => 9, 'etat' => 'active', 'prochaine' => 0, 'fin' => 0]], $now, 180));
        $this->expectException(\InvalidArgumentException::class);
        EcheancesRegles::echeances([], $now, 31);
    }

    public function testPaiementsNatifsTriDatePuisIdEtExclusions(): void
    {
        $base = ['etat' => 'on-hold', 'paye' => false, 'date_payee' => 0, 'methode' => 'bacs', 'creation' => 10];
        $rows = [
            $base + ['id' => 10], $base + ['id' => 2],
            array_replace($base, ['id' => 11, 'etat' => 'pending', 'methode' => 'stripe', 'creation' => 9]),
            array_replace($base, ['id' => 12, 'etat' => 'failed', 'creation' => 8]),
            array_replace($base, ['id' => 13, 'etat' => 'completed', 'paye' => true, 'date_payee' => 1]),
            array_replace($base, ['id' => 14, 'date_payee' => 1]),
            array_replace($base, ['id' => 15, 'etat' => 'cancelled']),
            array_replace($base, ['id' => 16, 'etat' => 'refunded']),
            array_replace($base, ['id' => 17, 'etat' => 'pending', 'methode' => '', 'creation' => 3]),
        ];
        self::assertSame([17, 11, 2, 10], array_column(EcheancesRegles::paiements($rows, 'attente'), 'id'));
        self::assertSame([2, 10], array_column(EcheancesRegles::paiements($rows, 'virements'), 'id'));
        self::assertSame([12], array_column(EcheancesRegles::paiements($rows, 'echecs'), 'id'));
        $this->expectException(\InvalidArgumentException::class);
        EcheancesRegles::paiements([], 'autre');
    }

    public function testMandatsActifsSeulementEtFinNonRenouvelable(): void
    {
        $base = ['id' => 1, 'etat' => 'active', 'methode' => 'imagine_papier', 'reference' => 'FICTIF', 'prochaine' => 99, 'fin' => 200];
        self::assertSame([1], array_column(EcheancesRegles::mandats([$base], 100, 30), 'id'));
        foreach ([['methode' => 'bacs'], ['etat' => 'pending-cancel'], ['etat' => 'pending'], ['etat' => 'cancelled'], ['fin' => 99]] as $change) {
            self::assertSame([], EcheancesRegles::mandats([array_replace($base, $change)], 100, 30));
        }
        $this->expectException(\InvalidArgumentException::class);
        EcheancesRegles::mandats([], 100, 31);
    }

    public function testCsvColonnesFermeesDeviseFormulesEtUtcSansIban(): void
    {
        $stream = fopen('php://memory', 'w+');
        EcheancesRegles::csv($stream, [['abonne' => " \t=FORMULE", 'montant' => '60.00', 'devise' => 'EUR',
            'reference' => '+FICTIF', 'echeance' => 1795608000, 'iban' => 'INTERDIT']]);
        rewind($stream);
        $csv = stream_get_contents($stream);
        rewind($stream);
        self::assertSame(['Abonné', 'Montant', 'Devise', 'Référence du mandat', 'Échéance (UTC)'], fgetcsv($stream, 0, ';', '"', ''));
        $line = fgetcsv($stream, 0, ';', '"', '');
        self::assertSame("' \t=FORMULE", $line[0]);
        self::assertSame("'+FICTIF", $line[3]);
        self::assertSame('EUR', $line[2]);
        self::assertSame('2026-11-25 12:00:00', $line[4]);
        self::assertStringNotContainsString('INTERDIT', $csv);
        fclose($stream);
    }

    public function testMandatSuspenduExigeRenouvellementNatifDuEtSupprimeLeFutur(): void
    {
        $base = ['id' => 9, 'etat' => 'on-hold', 'methode' => 'imagine_papier',
            'prochaine' => 200, 'fin' => 0, 'reference' => 'FICTIF', 'abonne' => 'Fictif',
            'montant' => '99.00', 'devise' => 'EUR'];
        $due = ['id' => 41, 'etat' => 'pending', 'paye' => false, 'date_payee' => 0,
            'creation' => 99, 'montant' => '12.34', 'devise' => 'EUR'];
        $rows = EcheancesRegles::mandats([$base + ['renouvellements' => [$due, $due]]], 100, 30);
        self::assertCount(1, $rows);
        self::assertSame(41, $rows[0]['id']);
        self::assertSame(99, $rows[0]['echeance']);
        self::assertSame('12.34', $rows[0]['montant']);
        self::assertSame(9, $rows[0]['souscription']);
        self::assertSame([], EcheancesRegles::mandats([$base], 100, 30));
        foreach ([['paye' => true], ['date_payee' => 1], ['creation' => 101], ['etat' => 'cancelled']] as $change) {
            self::assertSame([], EcheancesRegles::mandats([$base + ['renouvellements' => [array_replace($due, $change)]]], 100, 30));
        }
        $active = array_replace($base, ['etat' => 'active', 'renouvellements' => [$due]]);
        self::assertSame([41], array_column(EcheancesRegles::mandats([$active], 100, 30), 'id'));
        $active['renouvellements'][0]['paye'] = true;
        self::assertSame([9], array_column(EcheancesRegles::mandats([$active], 100, 30), 'id'));
    }

    public function testMandatSansReferenceResteVisibleEtExporte(): void
    {
        $row = ['id' => 1, 'etat' => 'active', 'methode' => 'imagine_papier',
            'prochaine' => 100, 'fin' => 0, 'reference' => '', 'abonne' => 'Fictif',
            'montant' => '60.00', 'devise' => 'EUR'];
        $rows = EcheancesRegles::mandats([$row], 100, 30);
        self::assertCount(1, $rows);
        self::assertSame('Référence manquante', $rows[0]['reference']);
        $stream = fopen('php://memory', 'w+');
        EcheancesRegles::csv($stream, $rows);
        rewind($stream);
        self::assertStringContainsString('Référence manquante', stream_get_contents($stream));
        fclose($stream);
    }
}
