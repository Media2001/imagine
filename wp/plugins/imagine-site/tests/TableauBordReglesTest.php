<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\TableauBordRegles;
use PHPUnit\Framework\TestCase;

final class TableauBordReglesTest extends TestCase
{
    public function testEntryUsesNativeCreationAsStandardNewSubscriptionsNotScheduleStart(): void
    {
        $now = strtotime('2026-11-26 12:00:00 UTC');
        $r = TableauBordRegles::calculer('mouvements', ['maintenant' => $now, 'mouvements' => [
            ['creation' => $now, 'debut' => strtotime('2025-01-01 UTC'), 'fin' => 0, 'etat' => 'pending'],
            ['creation' => strtotime('2025-01-01 UTC'), 'debut' => $now, 'fin' => 0, 'etat' => 'active'],
            ['creation' => $now, 'debut' => 0, 'fin' => 0, 'etat' => 'active'],
        ]]);
        self::assertSame(2, $r['valeurs']['entrees']);
        self::assertStringContainsString('création native', $r['phrase']);
    }

    public function testEmptySourcesGiveRealZerosAndUnknownIndicatorIsRefused(): void
    {
        $data = ['abonnements' => [], 'echeances' => [], 'echecs' => [], 'mouvements' => [], 'maintenant' => 1800000000];
        self::assertCount(4, TableauBordRegles::catalogue());
        foreach (array_keys(TableauBordRegles::catalogue()) as $id) {
            $r = TableauBordRegles::calculer($id, $data);
            self::assertNotEmpty($r['phrase']);
            foreach ($r['valeurs'] as $value) {
                self::assertSame(0, $value);
            }
        }
        $this->expectException(\InvalidArgumentException::class);
        TableauBordRegles::calculer('../secret', $data);
    }

    public function testMonthCountsNativeDatesWithoutInventingTransitions(): void
    {
        self::assertArrayHasKey('mouvements', TableauBordRegles::catalogue());
        $now = strtotime('2026-11-26 12:00:00 UTC');
        $begin = strtotime('2026-11-01 UTC');
        $rows = [
            ['debut' => $begin, 'fin' => 0, 'etat' => 'active'],
            ['debut' => $begin - 1, 'fin' => $begin, 'etat' => 'expired'],
            ['debut' => $now, 'fin' => $now, 'etat' => 'cancelled'],
            ['debut' => $now + 1, 'fin' => $now + 1, 'etat' => 'expired'],
            ['debut' => 0, 'fin' => $now, 'etat' => 'pending-cancel'],
            ['debut' => strtotime('2026-12-01 UTC'), 'fin' => 0, 'etat' => 'pending'],
        ];
        $rows = array_map(static fn (array $row): array => $row + ['creation' => $row['debut']], $rows);
        $data = ['mouvements' => $rows, 'maintenant' => $now];
        $saved = $data;
        $r = TableauBordRegles::calculer('mouvements', $data);
        self::assertSame(['entrees' => 2, 'sorties' => 2], $r['valeurs']);
        self::assertSame($saved, $data);
        self::assertStringContainsString('UTC', $r['phrase']);
        self::assertStringContainsString('historique', $r['phrase']);
    }

    public function testFailedPaymentsReuseC15UnpaidSelection(): void
    {
        self::assertArrayHasKey('echecs', TableauBordRegles::catalogue());
        $base = ['id' => 1, 'etat' => 'failed', 'paye' => false, 'date_payee' => 0, 'creation' => 10];
        $rows = [$base, array_replace($base, ['id' => 2, 'paye' => true]),
            array_replace($base, ['id' => 3, 'date_payee' => 20]), array_replace($base, ['id' => 4, 'etat' => 'pending'])];
        $r = TableauBordRegles::calculer('echecs', ['echecs' => $rows]);
        self::assertSame(['total' => 1], $r['valeurs']);
        self::assertSame(count(\Imagine\Site\EcheancesRegles::paiements($rows, 'echecs')), $r['valeurs']['total']);
    }

    public function testDueWindowsReuseC15BoundsAndStatuses(): void
    {
        self::assertArrayHasKey('echeances', TableauBordRegles::catalogue());
        $now = 1800000000;
        $rows = [];
        foreach ([0, 30, 31, 90, 91, 180, 181] as $id => $days) {
            $rows[] = ['id' => $id, 'etat' => 'active', 'prochaine' => $now + $days * 86400, 'fin' => 0];
        }
        $rows[] = ['id' => 99, 'etat' => 'cancelled', 'prochaine' => $now, 'fin' => 0];
        $r = TableauBordRegles::calculer('echeances', ['echeances' => $rows, 'maintenant' => $now]);
        self::assertSame(['30' => 2, '90' => 4, '180' => 6], $r['valeurs']);
        foreach ([30, 90, 180] as $days) {
            self::assertSame(count(\Imagine\Site\EcheancesRegles::echeances($rows, $now, $days)), $r['valeurs'][$days]);
        }
    }

    public function testActiveNumbersReuseExtractionStateAndNeverInferBlankMethod(): void
    {
        self::assertTrue(class_exists(TableauBordRegles::class), 'Moteur pur C19 manquant');
        $rows = [['etat' => 'Actif', 'mode_paiement' => 'bacs'],
            ['etat' => 'Actif', 'mode_paiement' => ''],
            ['etat' => 'Suspendu', 'mode_paiement' => 'bacs'],
            ['etat' => 'En délai de grâce', 'mode_paiement' => 'imagine_papier']];
        $result = TableauBordRegles::calculer('actifs', ['abonnements' => $rows]);
        self::assertSame(['total' => 2, 'mode:bacs' => 1, 'mode:inconnu' => 1], $result['valeurs']);
        self::assertStringContainsString('C18', $result['phrase']);
        self::assertStringContainsString('abonnement', $result['phrase']);
    }
}
