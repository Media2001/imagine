<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\ComptesPublicsRegles;
use PHPUnit\Framework\TestCase;

final class ComptesPublicsC33Test extends TestCase
{
    public function testRoutesFermeesSansPrefixeApproximatif(): void
    {
        foreach (['/wp/v2/users', '/wp/v2/users/123', '/WP/V2/USERS/123', '/wp/v2/users/me', '/wp/v2/users/'] as $route) {
            self::assertTrue(ComptesPublicsRegles::utilisateurs($route));
        }
        foreach (['/wp/v2/users-extra', '/wp/v2/posts/123', '/autre/wp/v2/users'] as $route) {
            self::assertFalse(ComptesPublicsRegles::utilisateurs($route));
        }
    }

    public function testSignatureOuSiteJamaisCompte(): void
    {
        self::assertSame('Signature fictive', ComptesPublicsRegles::signature(' Signature fictive ', 'SITE'));
        foreach (['', '   ', null, [], false] as $value) {
            self::assertSame('SITE', ComptesPublicsRegles::signature($value, 'SITE'));
        }
    }
}
