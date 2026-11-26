<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Soutenir;
use Imagine\Site\Cooperative;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class SoutenirAdapterTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/SujetWPStubs.php';
    }

    public function testDonFermePuisOuvertLienPartsEtOrdre(): void
    {
        self::assertTrue(class_exists(Soutenir::class), 'Soutenir absent');
        $html = Soutenir::rendre();
        self::assertStringContainsString('abonnement', $html);
        self::assertStringContainsString('bénévolat', $html);
        self::assertStringContainsString('prise de parts', $html);
        self::assertStringNotContainsString('don ponctuel', $html);
        self::assertStringNotContainsString('sponsored', $html);
        self::assertStringNotContainsString('iframe', $html);
        self::assertSame(['don' => false, 'parts_url' => ''], Soutenir::configuration());
        $GLOBALS['b08_options'][Soutenir::OPTION] = ['don' => true, 'parts_url' => 'https://example.org/parts'];
        $html = Soutenir::rendre();
        self::assertStringContainsString('don ponctuel ou récurrent', $html);
        self::assertStringContainsString('sans paiement', $html);
        self::assertStringContainsString('rel="sponsored"', $html);
        self::assertStringContainsString('https://example.org/parts', $html);
        $positions = array_map(static fn ($text) => strpos($html, $text), ['abonnement', 'don ponctuel', 'bénévolat', 'prise de parts']);
        $sorted = $positions;
        sort($sorted);
        self::assertSame($sorted, $positions);
        self::assertSame(['don' => false, 'parts_url' => ''], Soutenir::nettoyer(['don' => '0', 'parts_url' => '']));
        self::assertSame(Soutenir::configuration(), Soutenir::nettoyer(['don' => '1', 'parts_url' => 'javascript:alert(1)']));
        self::assertSame(['don' => true, 'parts_url' => 'https://example.org/parts'], Soutenir::nettoyer(['don' => '1', 'parts_url' => 'https://example.org/parts']));
        self::assertStringContainsString('imagine_soutenir[parts_url]', Soutenir::champs());
    }

    public function testNavigationNativeVideEtLienB06SansChangerAcces(): void
    {
        self::assertTrue(class_exists(Cooperative::class), 'Raccord pages absent');
        $html = Cooperative::rendre(1, '');
        foreach (\Imagine\Site\CooperativeRegles::PAGES as $title) {
            self::assertStringContainsString(htmlspecialchars($title, ENT_QUOTES, 'UTF-8'), $html);
        }
        self::assertStringContainsString('Espace coopérateurs', $html);
        self::assertStringContainsString('Proposer un sujet', $html);
        self::assertStringContainsString('Notre coopérative', Cooperative::rendre(10, ''));
        self::assertSame('Témoin', Cooperative::rendre(999, 'Témoin'));
    }
}
