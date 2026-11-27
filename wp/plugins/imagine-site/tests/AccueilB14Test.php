<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Accueil;
use PHPUnit\Framework\TestCase;

final class AccueilB14Test extends TestCase
{
    public function testEvenementsConserventOrdreAvecMaximumTrois(): void
    {
        self::assertSame([], Accueil::premiersEvenements([]));
        self::assertSame([1, 2], Accueil::premiersEvenements([1, 2]));
        self::assertSame([1, 2, 3], Accueil::premiersEvenements([1, 2, 3, 4, 5]));
    }
}
