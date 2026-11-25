<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\EcheancesRegles;
use PHPUnit\Framework\TestCase;

final class EcheancesReglesTest extends TestCase
{
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
