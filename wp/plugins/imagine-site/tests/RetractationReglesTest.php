<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\RetractationRegles;
use PHPUnit\Framework\TestCase;

final class RetractationReglesTest extends TestCase
{
    public function testDelaiEtOriginesAvecBornesEtFermeturePrudente(): void
    {
        self::assertTrue(class_exists(RetractationRegles::class), 'Règle C25 absente');
        foreach ([1, 14, 30, 365] as $days) {
            foreach (['paiement', 'manuelle'] as $origin) {
                $config = ['jours' => $days, 'origine' => $origin];
                $start = $origin === 'paiement' ? 100000 : 200000;
                foreach ([$start - 1 => false, $start => true, $start + $days * 86400 => true, $start + $days * 86400 + 1 => false] as $now => $expected) {
                    self::assertSame($expected, RetractationRegles::ouverte($config, 100000, 200000, $now));
                }
            }
        }
        self::assertFalse(RetractationRegles::ouverte(['jours' => 14, 'origine' => 'paiement'], null, 200000, 200001));
        self::assertFalse(RetractationRegles::ouverte(['jours' => 14, 'origine' => 'manuelle'], 100000, null, 100001));
        foreach ([0, -1, 366, '14', 1.5] as $bad) {
            self::assertFalse(RetractationRegles::ouverte(['jours' => $bad, 'origine' => 'paiement'], 100000, null, 100001));
        }
        self::assertFalse(RetractationRegles::ouverte(['jours' => 14, 'origine' => 'inconnue'], 100000, null, 100001));
    }
}
