<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\CooperativeRegles;
use PHPUnit\Framework\TestCase;

final class CooperativeReglesTest extends TestCase
{
    public function testTitresExactsEtOrdreCDC(): void
    {
        self::assertTrue(class_exists(CooperativeRegles::class), 'Structure B08 absente');
        self::assertSame(['projet éditorial et manifeste', "charte d'indépendance", 'charte IA', 'baromètre égalité-diversité', 'équipe', 'gouvernance', 'Imagine COOP'], array_values(CooperativeRegles::PAGES));
        self::assertSame(['abonnement', 'don', 'bénévolat', 'prise de parts'], CooperativeRegles::SOUTIEN);
    }
}
