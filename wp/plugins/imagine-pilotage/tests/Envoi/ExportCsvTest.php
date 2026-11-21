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

    public function testProtectionC04PartageeSansChangerSonComportement(): void
    {
        foreach (['=1', '+1', '-1', '@x', "\t=1", "\r\n +1", "\x00@x", 'normal', '00100', ''] as $cellule) {
            $attendu = preg_match('/\\A[\\x00-\\x20]*[=+@-]/', $cellule) === 1
                ? "'" . $cellule : $cellule;
            self::assertSame($attendu, CsvProtection::cellule($cellule));
        }
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
