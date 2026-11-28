<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\DomainesRefusesRegles;
use PHPUnit\Framework\TestCase;

final class DomainesRefusesC31Test extends TestCase
{
    public function testDomainesExactsSansCasseNiHeritage(): void
    {
        $list = DomainesRefusesRegles::liste("JETABLE-FICTIF.example.org\njetable-fictif.example.org\n");
        self::assertSame(['jetable-fictif.example.org'], $list);
        self::assertTrue(DomainesRefusesRegles::refuse('fictif@JETABLE-FICTIF.example.org', $list));
        self::assertFalse(DomainesRefusesRegles::refuse('fictif@sub.jetable-fictif.example.org', $list));
        self::assertFalse(DomainesRefusesRegles::refuse('fictif@jetable-fictif.example.org', []));
    }

    public function testConfigurationInvalideNonReparee(): void
    {
        foreach (["https://example.org", "*.example.org", "example.org.", "fictif\\.example.org", "fictif@example.org"] as $input) {
            self::assertNull(DomainesRefusesRegles::liste($input));
        }
        self::assertSame([], DomainesRefusesRegles::liste(''));
    }
}
