<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Navigation;
use PHPUnit\Framework\TestCase;

final class NavigationB13Test extends TestCase
{
    public function testReglageFermeEtBorne(): void
    {
        self::assertSame(3, Navigation::nombre('aucun'));
        self::assertSame(3, Navigation::nombre([]));
        self::assertSame(3, Navigation::nombre(null));
        self::assertSame(3, Navigation::nombre(3));
        self::assertSame(1, Navigation::nombre(0));
        self::assertSame(10, Navigation::nombre(40));
    }
}
