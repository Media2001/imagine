<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\AgendaRegles;
use PHPUnit\Framework\TestCase;

final class AgendaReglesTest extends TestCase
{
    public function testInscriptionGratuiteSansRegleMarketing(): void
    {
        foreach (['rencontre', 'sortie'] as $type) {
            self::assertTrue(AgendaRegles::inscription($type, 200, 100));
            self::assertFalse(AgendaRegles::inscription($type, 100, 100));
            self::assertFalse(AgendaRegles::inscription($type, 99, 100));
        }
        self::assertFalse(AgendaRegles::inscription('partenaire', 200, 100));
        self::assertFalse(AgendaRegles::inscription('inconnu', 200, 100));
        self::assertFalse(AgendaRegles::inscription('rencontre', 0, 100));
    }

    public function testCleAntiDoublonSansAdresseEtCompatibleMysql(): void
    {
        $key = AgendaRegles::cle(42, ' FICTIF@EXAMPLE.ORG ');
        self::assertSame($key, AgendaRegles::cle(42, 'fictif@example.org'));
        self::assertNotSame($key, AgendaRegles::cle(43, 'fictif@example.org'));
        self::assertLessThanOrEqual(64, strlen($key));
        self::assertStringNotContainsString('fictif', $key);
        self::assertSame('fictif@example.org', AgendaRegles::email(' FICTIF@EXAMPLE.ORG '));
    }
}
