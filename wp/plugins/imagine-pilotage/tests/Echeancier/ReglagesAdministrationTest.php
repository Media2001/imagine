<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Echeancier;

use Imagine\Pilotage\Echeancier\ReglagesAdministration;
use PHPUnit\Framework\TestCase;

final class ReglagesAdministrationTest extends TestCase
{
    public function testRefusAdministrationUtiliseWpDieAvecTraduction(): void
    {
        require_once __DIR__ . '/FonctionsWordPressFictives.php';
        WordPressFictif::$appels = [];
        ob_start();
        try {
            (new ReglagesAdministration())->afficher();
            self::fail('Le refus WordPress doit terminer le rendu.');
        } catch (\Throwable $error) {
            self::assertInstanceOf(\RuntimeException::class, $error);
            self::assertSame('WP_DIE_TEST', $error->getMessage());
        } finally {
            $html = ob_get_clean();
        }
        self::assertSame('', $html);
        self::assertSame('manage_woocommerce', WordPressFictif::$appels['capacite']);
        self::assertSame(
            ['Gestion WooCommerce requise.', 'imagine-pilotage'],
            WordPressFictif::$appels['traduction']
        );
        self::assertSame('TRADUIT : Gestion WooCommerce requise.', WordPressFictif::$appels['wp_die']);
    }
}
