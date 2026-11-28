<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Cookies;
use PHPUnit\Framework\TestCase;

final class CookiesC32Test extends TestCase
{
    public function testListeFermeeEtMotifsAncres(): void
    {
        self::assertCount(14, Cookies::liste());
        $h = str_repeat('a', 32);
        self::assertSame([], Cookies::inconnus(['sbjs_session', 'wordpress_' . $h, 'wordpress_logged_in_' . $h, 'wp_woocommerce_session_' . $h, 'woocommerce_cart_hash']));
        foreach (['sbjs_intrus', 'wordpress_fake', 'prefix_sbjs_session', 'sbjs_session_suffix', "sbjs_session\n", 'sonde_cookie_interdit'] as $name) {
            self::assertSame([$name], Cookies::inconnus([$name]));
        }
    }
}
