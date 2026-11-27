<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\AcquisitionRegles;
use PHPUnit\Framework\TestCase;

final class AcquisitionReglesTest extends TestCase
{
    public function testListeFermeeEtPeriodeComptentLesReponsesPasLesIdentites(): void
    {
        self::assertTrue(method_exists(AcquisitionRegles::class, 'liste'), 'Liste C27 absente');
        self::assertSame([], AcquisitionRegles::liste([]));
        self::assertSame(['lune' => 'Radio fictive \\ lune'], AcquisitionRegles::liste(['lune' => 'Radio fictive \\ lune']));
        foreach ([['libre' => '<script>x</script>'], ['bad key' => 'Fictif'], ['x' => ''], ['x' => str_repeat('é', 81)], range(1, 21), 'texte'] as $bad) {
            self::assertNull(AcquisitionRegles::liste($bad));
        }
        $rows = [
            ['date' => '2026-11-01T00:00:00Z', 'choix' => 'lune', 'libelle' => 'Radio fictive'],
            ['date' => '2026-11-30T23:59:59Z', 'choix' => 'lune', 'libelle' => 'Radio fictive'],
            ['date' => '2026-12-01T00:00:00Z', 'choix' => 'mars', 'libelle' => 'Journal fictif'],
            ['date' => '2026-11-20T00:00:00Z', 'etat' => 'effacee'],
        ];
        self::assertSame([['choix' => 'lune', 'libelle' => 'Radio fictive', 'nombre' => 2]], AcquisitionRegles::compter($rows, '2026-11-01', '2026-11-30'));
        self::assertNull(AcquisitionRegles::compter($rows, '2026-11-31', '2026-12-01'));
        self::assertNull(AcquisitionRegles::compter($rows, '2026-12-01', '2026-11-01'));
    }

    public function testPaiementProprietaireEtCommandeOperateurFermentAvantTouteEcriture(): void
    {
        self::assertTrue(class_exists(AcquisitionRegles::class), 'Règle C27 absente');
        self::assertTrue(AcquisitionRegles::eligible(28, 28, true, true, 'checkout'));
        self::assertFalse(AcquisitionRegles::eligible(28, 28, false, true, 'checkout'));
        self::assertFalse(AcquisitionRegles::eligible(28, 28, true, false, 'checkout'));
        self::assertFalse(AcquisitionRegles::eligible(28, 29, true, true, 'checkout'));
        self::assertFalse(AcquisitionRegles::eligible(0, 0, true, true, 'checkout'));
        self::assertFalse(AcquisitionRegles::eligible(28, 28, true, true, 'imagine-c16'));
    }
}
