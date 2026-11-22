<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Envoi;

use Imagine\Pilotage\Envoi\AdministrationFormatExport;
use Imagine\Pilotage\Envoi\AdministrationFictive;
use Imagine\Pilotage\Envoi\ExportCsv;
use PHPUnit\Framework\TestCase;

final class AdministrationFormatExportTest extends TestCase
{
    protected function setUp(): void
    {
        require_once __DIR__ . '/AdministrationFictive.php';
        AdministrationFictive::$option = null;
        AdministrationFictive::$appels = [];
        AdministrationFictive::$autorise = true;
    }

    public function testAdaptateurSettingsApiAutonomeFormulaireProtegeEtExportConfigure(): void
    {
        $administration = new AdministrationFormatExport();
        $administration->brancher();
        self::assertSame('admin_menu', AdministrationFictive::$appels['action'][0][0]);
        self::assertSame('admin_init', AdministrationFictive::$appels['action'][1][0]);
        $administration->menu();
        self::assertSame('manage_options', AdministrationFictive::$appels['menu'][0][2]);
        $administration->enregistrer();
        $reglage = AdministrationFictive::$appels['reglage'][0];
        self::assertSame(AdministrationFormatExport::OPTION, $reglage[0]);
        self::assertSame(AdministrationFormatExport::OPTION, $reglage[1]);
        self::assertSame(ExportCsv::COLONNES, $reglage[2]['default']);
        self::assertSame('array', $reglage[2]['type']);
        self::assertFalse($reglage[2]['show_in_rest']);
        self::assertSame([$administration, 'nettoyer'], $reglage[2]['sanitize_callback']);
        AdministrationFictive::$option = ['pays', 'code_postal'];
        ob_start();
        $administration->page();
        $html = ob_get_clean();
        self::assertStringContainsString('action="options.php"', $html);
        self::assertStringContainsString('name="' . AdministrationFormatExport::OPTION . '"', $html);
        self::assertStringContainsString("pays\ncode_postal</textarea>", $html);
        self::assertSame([AdministrationFormatExport::OPTION], AdministrationFictive::$appels['nonce']);
        self::assertCount(1, AdministrationFictive::$appels['bouton']);
        ($reglage[2]['sanitize_callback'])("pays\nville");
        $date = static fn (string $d): \DateTimeImmutable => new \DateTimeImmutable($d);
        $numero = new \Imagine\Pilotage\Numeros\Numero(
            '171',
            \Imagine\Pilotage\Numeros\TypeNumero::Regulier,
            $date('2027-01-05'),
            $date('2026-12-20'),
        );
        $liste = \Imagine\Pilotage\Envoi\ListeEnvoi::etablir(
            $numero,
            new \Imagine\Pilotage\Numeros\Calendrier([$numero]),
            [],
            $numero->cloture,
        );
        self::assertSame("pays,code_postal\n", $administration->exporter($liste));
        AdministrationFictive::$autorise = false;
        ob_start();
        $administration->page();
        self::assertSame('', ob_get_clean());
    }

    public function testToutesLesColonnesEtOrdreInverseSontAdministrables(): void
    {
        $administration = new AdministrationFormatExport();
        foreach (ExportCsv::COLONNES as $colonne) {
            AdministrationFictive::$option = $administration->nettoyer($colonne);
            self::assertSame([$colonne], $administration->lire()->colonnes);
        }
        $inverse = array_reverse(ExportCsv::COLONNES);
        AdministrationFictive::$option = $administration->nettoyer(implode("\n", $inverse));
        self::assertSame($inverse, $administration->lire()->colonnes);
    }

    public static function saisiesInvalides(): array
    {
        return [
            [''], ["pays\npays"], ["pays\n=1"], ["pays\n\nville"],
            [false], [null], [12], [['email']], [['pays', 'pays']],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('saisiesInvalides')]
    public function testSaisieInvalideConserveDernierReglageEtSignaleErreur(mixed $valeur): void
    {
        AdministrationFictive::$option = ['pays', 'ville'];
        $administration = new AdministrationFormatExport();
        self::assertSame(['pays', 'ville'], $administration->nettoyer($valeur));
        self::assertCount(1, AdministrationFictive::$appels['erreur']);
        self::assertSame(AdministrationFormatExport::OPTION, AdministrationFictive::$appels['erreur'][0][0]);
    }

    public function testOptionCorrompueRevientAuxColonnesProvisoires(): void
    {
        $administration = new AdministrationFormatExport();
        foreach ([false, 'pays', [], ['email'], ['pays', 'pays']] as $valeur) {
            AdministrationFictive::$option = $valeur;
            self::assertSame(ExportCsv::COLONNES, $administration->lire()->colonnes);
        }
    }

    public function testReglageTexteSansCodeNormaliseEtReluDansOrdreChoisi(): void
    {
        $administration = new AdministrationFormatExport();
        self::assertSame(ExportCsv::COLONNES, $administration->lire()->colonnes);
        $valeur = $administration->nettoyer("pays\r\ncode_postal\r\ndestinataire");
        self::assertSame(['pays', 'code_postal', 'destinataire'], $valeur);
        self::assertSame($valeur, $administration->nettoyer($valeur));
        AdministrationFictive::$option = $valeur;
        self::assertSame($valeur, (new AdministrationFormatExport())->lire()->colonnes);
        self::assertSame([], AdministrationFictive::$appels);
    }
}
