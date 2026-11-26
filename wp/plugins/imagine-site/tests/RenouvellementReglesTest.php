<?php

declare(strict_types=1);
namespace Imagine\Site\Tests;
use PHPUnit\Framework\TestCase;
use Imagine\Site\RenouvellementRegles;

final class RenouvellementReglesTest extends TestCase
{
    public function testQuatreFoisGardeLaDemandeChezImagine(): void
    {
        $view = RenouvellementRegles::presentation(['status'=>'active','manual'=>true,'period'=>'month','interval'=>3,'end'=>'2027-01-01 00:00:00'], new \DateTimeImmutable('2026-11-26 UTC'));
        self::assertSame('quatre_fois', $view['mode']);
        self::assertFalse($view['arreter']);
        self::assertFalse($view['reprendre']);
        self::assertSame('Pour ne pas renouveler votre engagement en quatre fois, faites la demande auprès d’Imagine ; les échéances du bloc en cours restent dues.', $view['message']);
    }

    public function testMandatManuelPrimeSurLaPeriodiciteTrimestrielle(): void
    {
        $view = RenouvellementRegles::presentation(['status'=>'active','manual'=>true,'method'=>'imagine_papier','period'=>'month','interval'=>3], new \DateTimeImmutable('2026-11-26 UTC'));
        self::assertSame('manuel', $view['mode']);
    }

    public function testAutomatiqueNonProuveNePretendPasEtreManuel(): void
    {
        $view = RenouvellementRegles::presentation(['status'=>'active','manual'=>false,'method'=>'stripe','period'=>'year','interval'=>1], new \DateTimeImmutable('2026-11-26 UTC'));
        self::assertSame('indisponible', $view['mode']);
        self::assertFalse($view['arreter']);
        self::assertFalse($view['reprendre']);
    }

    public function testAnnulationATermeAfficheLaFinSansPromettreLaReprise(): void
    {
        $view = RenouvellementRegles::presentation(['status'=>'pending-cancel','manual'=>true,'period'=>'year','interval'=>1,'end'=>'2026-12-25 18:01:50'], new \DateTimeImmutable('2026-11-26 UTC'));
        self::assertSame('arret_a_terme', $view['mode']);
        self::assertSame('2026-12-25 18:01:50', $view['fin']);
        self::assertFalse($view['reprendre']);
    }

    public function testManuelNeProposeAucunBouton(): void
    {
        self::assertTrue(class_exists(RenouvellementRegles::class), 'Présentation C20 absente');
        $view = RenouvellementRegles::presentation(['status'=>'active','manual'=>true,'period'=>'year','interval'=>1,'end'=>'2027-01-01 00:00:00'], new \DateTimeImmutable('2026-11-26 UTC'));
        self::assertSame('manuel', $view['mode']);
        self::assertFalse($view['arreter']);
        self::assertFalse($view['reprendre']);
        self::assertStringContainsString('manuel', $view['message']);
    }
}
