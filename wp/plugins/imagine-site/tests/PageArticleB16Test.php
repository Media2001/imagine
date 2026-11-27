<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\PageArticle;
use PHPUnit\Framework\TestCase;

final class PageArticleB16Test extends TestCase
{
    public function testAppelSeulementCompletSansAbonnement(): void
    {
        self::assertTrue(PageArticle::appel(['complet' => true], false));
        self::assertFalse(PageArticle::appel(['complet' => true], true));
        self::assertFalse(PageArticle::appel(['complet' => false], false));
        self::assertFalse(PageArticle::appel([], false));
    }

    public function testUneValeurIndetermineeNeDonnePasUnAppelComplet(): void
    {
        self::assertFalse(PageArticle::appel(['complet' => 'true'], false));
        self::assertFalse(PageArticle::appel(['complet' => 1], false));
        self::assertFalse(PageArticle::appel(['complet' => null], false));
    }
}
