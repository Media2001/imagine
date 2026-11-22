<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Envoi;

use Imagine\Pilotage\Envoi\ExportCsv;
use Imagine\Pilotage\Envoi\FormatExport;
use PHPUnit\Framework\TestCase;

final class FormatExportTest extends TestCase
{
    public static function setUpBeforeClass(): void
    {
        ExportCsvTest::setUpBeforeClass();
    }

    public static function formatsInvalides(): array
    {
        return [
            'vide' => [[]],
            'champ inconnu' => [['email']],
            'formule en entete' => [['=1']],
            'repetition' => [['pays', 'pays']],
            'indice troue' => [[1 => 'pays']],
            'associatif' => [['champ' => 'pays']],
            'non texte' => [[1]],
            'espace non normalise' => [[' pays']],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('formatsInvalides')]
    public function testFormatInvalideRefuseSansCorrectionSilencieuse(array $colonnes): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new FormatExport($colonnes);
    }

    public function testChaqueColonnePeutEtreSelectionneeSeule(): void
    {
        $ligne = array_fill_keys(ExportCsv::COLONNES, 'CamilleFictive');
        foreach (ExportCsv::COLONNES as $colonne) {
            self::assertSame(
                $colonne . "\nCamilleFictive\n",
                ExportCsv::lignes([$ligne], new FormatExport([$colonne])),
            );
        }
    }

    public function testSelectionEtOrdreDesColonnesSansChangerLesValeurs(): void
    {
        ExportCsvTest::setUpBeforeClass();
        $ligne = array_fill_keys(ExportCsv::COLONNES, 'non selectionne');
        $ligne['pays'] = 'BE';
        $ligne['code_postal'] = '00100';
        $ligne['destinataire'] = '=Camille Fictive';
        $format = new FormatExport(['pays', 'code_postal', 'destinataire']);
        self::assertSame(
            "pays,code_postal,destinataire\nBE,00100,\"'=Camille Fictive\"\n",
            ExportCsv::lignes([$ligne], format: $format),
        );
        self::assertSame("pays,code_postal,destinataire\n", ExportCsv::lignes([], format: $format));
        self::assertSame(ExportCsv::lignes([$ligne]), ExportCsv::lignes([$ligne], format: new FormatExport()));
    }
}
