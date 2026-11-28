<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Cookies;
use PHPUnit\Framework\TestCase;

final class CookiesC32Test extends TestCase
{
    public function testSessionWooNeDeclarePasLaConnexionNonObservee(): void
    {
        $rows = array_column(Cookies::liste(), null, 'nom');
        self::assertSame('Code suivi connu (C-30), panier', $rows['wp_woocommerce_session_[hash]']['geste']);
    }

    public function testTraductionsExtractiblesEtDonneesNonTraduites(): void
    {
        $source = file_get_contents(dirname(__DIR__) . '/Cookies.php');
        self::assertDoesNotMatchRegularExpression('/esc_html__\\(\\s*\\$/', $source);
        foreach (['Nom ou motif', 'Déposé par', 'À quel geste', 'Durée', 'Usage'] as $heading) {
            self::assertStringContainsString("esc_html__('" . $heading . "', 'imagine-site')", $source);
        }
        self::assertStringContainsString('esc_html($row[$key])', $source);
    }

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
