<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Accueil;
use PHPUnit\Framework\TestCase;

final class AccueilB14Test extends TestCase
{
    #[\PHPUnit\Framework\Attributes\RunInSeparateProcess]
    #[\PHPUnit\Framework\Attributes\PreserveGlobalState(false)]
    public function testStructureReelleRendueAvecBouchonsMinimaux(): void
    {
        require __DIR__ . '/AccueilB14StructureFixture.php';
        ob_start();
        Accueil::rendre();
        $html = ob_get_clean();
        $doc = new \DOMDocument();
        @$doc->loadHTML('<?xml encoding="utf-8" ?>' . $html);
        $xpath = new \DOMXPath($doc);
        $order = [];
        foreach ($xpath->query('//body/section') as $section) {
            $order[] = $section->getAttribute('data-b14-section') ?: 'partenaire';
        }
        self::assertSame(['numero','conversion','reportage','newsletter','thematiques','evenements','soutenir','cooperative','partenaire'], $order);
        self::assertSame(1, $xpath->query('//img[@loading="eager" and @fetchpriority="high"]')->length);
        self::assertSame(1, $xpath->query('//img[@fetchpriority="high"]')->length);
        self::assertSame(1, $xpath->query('//img[@loading="eager"]')->length);
        self::assertSame(1, $xpath->query('//section[@id="imagine-abonnement"]')->length);
        self::assertSame(1, $xpath->query('//section[@id="imagine-abonnement"]//a[@href="https://example.invalid/attente/"]')->length);
        self::assertSame(0, $xpath->query('//video|//iframe')->length);
        self::assertStringNotContainsString('CONTENU_FICTIF_RESERVE_GARDE_B14', $html);
    }

    public function testEvenementsConserventOrdreAvecMaximumTrois(): void
    {
        self::assertSame([], Accueil::premiersEvenements([]));
        self::assertSame([1, 2], Accueil::premiersEvenements([1, 2]));
        self::assertSame([1, 2, 3], Accueil::premiersEvenements([1, 2, 3, 4, 5]));
    }
}
