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

    #[\PHPUnit\Framework\Attributes\RunInSeparateProcess]
    #[\PHPUnit\Framework\Attributes\PreserveGlobalState(false)]
    public function testRenduReelTraduitLesLitterauxSeulementEtGardeLeTexte(): void
    {
        require __DIR__ . '/CookiesC32Stubs.php';
        $GLOBALS['c32_translated'] = [];
        $content = '<p>Texte fictif &amp; conservé</p>';
        $html = Cookies::contenu($content);
        self::assertStringStartsWith($content, $html);
        self::assertSame(15, substr_count($html, '<tr>'));
        self::assertSame(1, substr_count($html, 'data-imagine-cookies'));
        self::assertCount(6, $GLOBALS['c32_translated']);
        foreach (Cookies::liste() as $row) {
            self::assertStringContainsString(htmlspecialchars($row['nom'], ENT_QUOTES, 'UTF-8'), $html);
            self::assertStringContainsString(htmlspecialchars($row['geste'], ENT_QUOTES, 'UTF-8'), $html);
        }
        self::assertStringNotContainsString('<script', $html);
        self::assertStringNotContainsString('ou connexion', $html);
    }

    #[\PHPUnit\Framework\Attributes\RunInSeparateProcess]
    #[\PHPUnit\Framework\Attributes\PreserveGlobalState(false)]
    public function testAucuneTableHorsDeLaPageCookies(): void
    {
        require __DIR__ . '/CookiesC32Stubs.php';
        $GLOBALS['c32_page_id'] = 31;
        $GLOBALS['c32_translated'] = [];
        self::assertSame('<p>Fictif</p>', Cookies::contenu('<p>Fictif</p>'));
        self::assertSame([], $GLOBALS['c32_translated']);
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
