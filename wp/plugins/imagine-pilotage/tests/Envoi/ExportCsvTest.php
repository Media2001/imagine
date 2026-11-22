<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Envoi;

use Imagine\Connecteur\CsvProtection;
use Imagine\Pilotage\Envoi\ExportCsv;
use PHPUnit\Framework\TestCase;

final class ExportCsvTest extends TestCase
{
    public static function setUpBeforeClass(): void
    {
        spl_autoload_register(static function (string $class): void {
            $prefix = 'Imagine\\Connecteur\\';
            if (!str_starts_with($class, $prefix)) {
                return;
            }
            $directory = dirname(__DIR__, 3) . '/imagine-connecteur/src';
            if (!is_dir($directory)) {
                $directory = dirname(__DIR__, 2) . '/connecteur';
            }
            $file = $directory . '/' . substr($class, strlen($prefix)) . '.php';
            if (is_file($file)) {
                require_once $file;
            }
        });
    }

    public static function cellulesCsv(): array
    {
        return [
            'egal' => ['=1', "'=1"],
            'plus' => ['+1', "'+1"],
            'moins' => ['-1', "'-1"],
            'arobase' => ['@x', "'@x"],
            'tabulation' => ["\t=1", "'\t=1"],
            'retours et espace' => ["\r\n +1", "'\r\n +1"],
            'nul' => ["\x00@x", "'\x00@x"],
            'controle' => ["\x1F-1", "'\x1F-1"],
            'espace' => [' =1', "' =1"],
            'normal' => ['normal', 'normal'],
            'zero initial' => ['00100', '00100'],
            'vide' => ['', ''],
            'formule non initiale' => ['texte=1', 'texte=1'],
            'apostrophe existante' => ["'=1", "'=1"],
            'ponctuation' => ['Fictive, "Camille"', 'Fictive, "Camille"'],
            'controle sans formule' => ["\tnormal", "\tnormal"],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('cellulesCsv')]
    public function testProtectionC04PartageeSansChangerSonComportement(string $cellule, string $attendu): void
    {
        self::assertSame($attendu, CsvProtection::cellule($cellule));
        $colonnes = [
            'abonnement_id', 'destinataire_id', 'destinataire', 'rue', 'complement',
            'code_postal', 'ville', 'pays', 'origine',
        ];
        $csv = ExportCsv::lignes([array_fill_keys($colonnes, $cellule)]);
        $stream = fopen('php://memory', 'w+b');
        fwrite($stream, $csv);
        rewind($stream);
        self::assertSame($colonnes, fgetcsv($stream, escape: ''));
        self::assertSame(array_fill(0, 9, $attendu), fgetcsv($stream, escape: ''));
        self::assertFalse(fgetcsv($stream, escape: ''));
        fclose($stream);
    }

    public function testCsvColonnesStablesInjectionEtRoundtrip(): void
    {
        $ligne = [
            'abonnement_id' => '=1', 'destinataire_id' => 'fictif', 'destinataire' => 'Camille "Fictive"',
            'rue' => "Rue Fictive, 1\nEtage 2", 'complement' => '\\', 'code_postal' => '00100',
            'ville' => 'Ville Fictive', 'pays' => 'BE', 'origine' => 'offert',
        ];
        $csv = ExportCsv::lignes([$ligne]);
        $stream = fopen('php://memory', 'w+b');
        fwrite($stream, $csv);
        rewind($stream);
        self::assertSame(ExportCsv::COLONNES, fgetcsv($stream, escape: ''));
        $valeurs = fgetcsv($stream, escape: '');
        self::assertSame("'=1", $valeurs[0]);
        self::assertSame(array_values(array_slice($ligne, 1)), array_slice($valeurs, 1));
        self::assertFalse(fgetcsv($stream, escape: ''));
        fclose($stream);
        self::assertSame($csv, ExportCsv::lignes([$ligne]));
    }

    public function testCsvVideGardeEntete(): void
    {
        self::assertSame(implode(',', ExportCsv::COLONNES) . "\n", ExportCsv::lignes([]));
    }
}
