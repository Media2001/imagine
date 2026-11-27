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

    public function testCorpsEtModeLectureRestentAuxAdaptateursExistants(): void
    {
        $single = file_get_contents(dirname(__DIR__, 3) . '/themes/imagine/single.php');
        self::assertSame(1, substr_count($single, 'imagine_article_body();'));
        self::assertStringContainsString('<header data-imagine-distraction data-b16="entete">', $single);
        self::assertStringContainsString('data-imagine-body="article"', $single);
        self::assertStringContainsString('Medias::rendre(get_post())', $single);
    }
}
