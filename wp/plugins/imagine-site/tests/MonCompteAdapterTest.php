<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\MonCompte;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunInSeparateProcess;
use PHPUnit\Framework\TestCase;

final class MonCompteAdapterTest extends TestCase
{
    private function charger(): void
    {
        require __DIR__ . '/b02-adapter-fixture.php';
        require_once dirname(__DIR__) . '/tests-c13/bootstrap.php';
        require_once dirname(__DIR__) . '/EnvoiNatif.php';
        require_once dirname(__DIR__) . '/EnvoiRelations.php';
        require_once dirname(__DIR__) . '/MonCompte.php';
    }

    #[RunInSeparateProcess]
    #[PreserveGlobalState(false)]
    public function testAbsenceMembershipsNeRendJamaisLeCompteFatal(): void
    {
        $this->charger();
        self::assertFalse(function_exists('wc_memberships_get_user_memberships'));
        try {
            $state = MonCompte::etat(new \WC_Subscription());
        } catch (\Throwable $error) {
            self::fail('Memberships absent : ' . $error->getMessage());
        }
        self::assertSame('Suspendu', $state);
    }

    #[RunInSeparateProcess]
    #[PreserveGlobalState(false)]
    public function testAdaptateurGardeLesQuatrePositionsSansCalendrierValideOuDebut(): void
    {
        $this->charger();
        $GLOBALS['b02_status'] = 'active';
        foreach ([null, [['sortie' => 'invalide']], []] as $calendar) {
            $GLOBALS['b02_calendar'] = $calendar;
            foreach (['2026-11-01 00:00:00', 'invalide'] as $start) {
                $GLOBALS['b02_start'] = $start;
                $data = MonCompte::donnees();
                self::assertCount(4, $data['abonnements'][0]['echeances']);
                self::assertNull($data['abonnements'][0]['premier']);
            }
        }
    }

    #[RunInSeparateProcess]
    #[PreserveGlobalState(false)]
    public function testGabaritNommeLeBlocIndisponibleEtLesRattachementsAmbigus(): void
    {
        $this->charger();
        $GLOBALS['b02_status'] = 'active';
        $compte = MonCompte::donnees();
        $compte['abonnements'][0]['avertissements'] = ['Rattachement ambigu — commande #30 (processing, 30.00 EUR)'];
        define('ABSPATH', '/fixture/');
        $template = dirname(__DIR__, 3) . '/themes/imagine/parts/mon-compte.php';
        if (!is_file($template)) {
            // T01 copie les seuls paquets ; le thème reste sur son montage source en lecture seule.
            $template = '/repo/wp/themes/imagine/parts/mon-compte.php';
        }
        self::assertFileExists($template);
        ob_start();
        try {
            require $template;
            $html = ob_get_contents();
        } finally {
            ob_end_clean();
        }
        self::assertStringContainsString('Bloc courant indisponible', $html);
        self::assertStringContainsString('Rattachement ambigu — commande #30', $html);
        self::assertSame(4, substr_count($html, '<th scope="row">'));
    }

    #[RunInSeparateProcess]
    #[PreserveGlobalState(false)]
    public function testMonCompteNeDupliquePasLeHookPostalDeEnvoiNatif(): void
    {
        $this->charger();
        MonCompte::register();
        self::assertNotContains('woocommerce_after_subscription_object_save', $GLOBALS['b02_hooks']);
    }
}
