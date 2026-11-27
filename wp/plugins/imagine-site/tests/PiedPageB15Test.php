<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\PiedPage;
use PHPUnit\Framework\TestCase;

final class PiedPageB15Test extends TestCase
{
    public function testOrdreDesCinqZonesEstUtiliseParLeRendu(): void
    {
        self::assertSame(['abonnement', 'newsletter', 'numero', 'point-vente', 'mentions'], PiedPage::ZONES);
    }

    #[\PHPUnit\Framework\Attributes\RunInSeparateProcess]
    #[\PHPUnit\Framework\Attributes\PreserveGlobalState(false)]
    public function testVraiRenduEtCachePuisMutationDuRetourAnticipe(): void
    {
        require __DIR__ . '/PiedPageB15Fixture.php';
        $GLOBALS['b15_cache'] = [];
        \Imagine\Site\Accueil::$builds = 0;
        ob_start();
        PiedPage::rendre();
        $first = (string)ob_get_clean();
        preg_match_all('/data-b15-zone="([^"]+)"/', $first, $zones);
        self::assertSame(['abonnement', 'newsletter', 'numero', 'point-vente', 'mentions'], $zones[1]);
        self::assertStringContainsString('FICTIF Numéro A', $first);
        self::assertSame(1, \Imagine\Site\Accueil::$builds);
        \Imagine\Site\Accueil::$title = 'FICTIF Numéro B';
        self::assertStringContainsString('FICTIF Numéro A', PiedPage::numero());
        self::assertSame(1, \Imagine\Site\Accueil::$builds);
        PiedPage::invalider();
        self::assertStringContainsString('FICTIF Numéro B', PiedPage::numero());
        self::assertSame(2, \Imagine\Site\Accueil::$builds);
        $source = file_get_contents(dirname(__DIR__) . '/PiedPage.php');
        $source = str_replace('final class PiedPage', 'final class PiedPageB15Mutant', $source);
        $source = str_replace('return $cached;', '/* retour anticipé supprimé */', $source);
        eval(substr($source, strpos($source, 'namespace')));
        $before = \Imagine\Site\Accueil::$builds;
        \Imagine\Site\PiedPageB15Mutant::numero();
        // Le même invariant « aucune construction si cache présent » devient faux.
        self::assertNotSame($before, \Imagine\Site\Accueil::$builds);
    }

    public function testContexteDeNavigationNeutraliseSeulementPourLePied(): void
    {
        $classes = ['menu-item', 'current-menu-item', 'current_page_parent', 'page_item', 'page-item-15', 'menu-item-15'];
        $attributes = ['href' => '/mentions/', 'aria-current' => 'page'];
        $item = new \stdClass();
        $footer = (object)['theme_location' => 'imagine-footer'];
        $header = (object)['theme_location' => 'imagine-principal'];
        self::assertSame(['menu-item', 'menu-item-15'], PiedPage::classes($classes, $item, $footer));
        self::assertSame($classes, PiedPage::classes($classes, $item, $header));
        self::assertSame(['href' => '/mentions/'], PiedPage::attributs($attributes, $item, $footer));
        self::assertSame($attributes, PiedPage::attributs($attributes, $item, $header));
    }
}
