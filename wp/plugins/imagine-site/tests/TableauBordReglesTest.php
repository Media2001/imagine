<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\TableauBordRegles;
use PHPUnit\Framework\TestCase;

final class TableauBordReglesTest extends TestCase
{
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
