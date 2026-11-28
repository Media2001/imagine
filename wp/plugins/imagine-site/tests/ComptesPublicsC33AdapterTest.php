<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\ComptesPublics;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class ComptesPublicsC33AdapterTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/ComptesPublicsC33WPStubs.php';
    }

    public function testEnregistrementExactPrioritesEtArguments(): void
    {
        ComptesPublics::register();
        self::assertSame([
            'template_redirect' => [[[ComptesPublics::class, 'auteur'], 0, 1]],
            'rest_pre_dispatch' => [[[ComptesPublics::class, 'rest'], 100, 3]],
            'wp_sitemaps_add_provider' => [[[ComptesPublics::class, 'sitemap'], 100, 2]],
            'the_author' => [[[ComptesPublics::class, 'auteurFlux'], 100, 1]],
            'get_the_author_user_url' => [[[ComptesPublics::class, 'adresseFlux'], 100, 1]],
            'oembed_response_data' => [[[ComptesPublics::class, 'oembed'], 100, 4]],
        ], $GLOBALS['c33_hooks']);
    }

    public function testArchiveFermeeAvantCanonicalEtGardesConnecteEtNonAuteur(): void
    {
        foreach ([[true, true], [false, false]] as [$logged, $author]) {
            $GLOBALS['c33_logged'] = $logged;
            $GLOBALS['c33_author'] = $author;
            ComptesPublics::auteur();
            self::assertSame([], $GLOBALS['c33_effects']);
        }
        $GLOBALS['c33_logged'] = false;
        $GLOBALS['c33_author'] = true;
        ComptesPublics::auteur();
        self::assertSame([
            ['set_404'],
            ['status_header', 404],
            ['nocache_headers'],
            ['remove_action', 'template_redirect', 'redirect_canonical', 10],
        ], $GLOBALS['c33_effects']);
    }

    public function testFiltresFluxNeTouchentNiHorsFluxNiConnectes(): void
    {
        foreach ([[false, false], [true, false], [true, true]] as [$logged, $feed]) {
            $GLOBALS['c33_logged'] = $logged;
            $GLOBALS['c33_feed'] = $feed;
            self::assertSame('COMPTE FICTIF', ComptesPublics::auteurFlux('COMPTE FICTIF'));
            self::assertSame('https://example.org/compte', ComptesPublics::adresseFlux('https://example.org/compte'));
        }
        $GLOBALS['c33_logged'] = false;
        $GLOBALS['c33_feed'] = true;
        self::assertSame('SITE &amp; FICTIF', ComptesPublics::auteurFlux('COMPTE FICTIF'));
        self::assertSame('', ComptesPublics::adresseFlux('https://example.org/compte'));
    }
}
