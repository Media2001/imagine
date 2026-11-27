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

    public function testContexteDeNavigationNeutraliseSeulementPourLePied(): void
    {
        $classes = ['menu-item', 'current-menu-item', 'current_page_parent', 'menu-item-15'];
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
