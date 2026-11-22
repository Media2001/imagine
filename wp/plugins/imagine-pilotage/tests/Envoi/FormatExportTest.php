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

    public function testPointEntreeListeAppliqueFormatEtGardeBarriereAnomalies(): void
    {
        $date = static fn (string $d): \DateTimeImmutable => new \DateTimeImmutable($d);
        $numero = new \Imagine\Pilotage\Numeros\Numero(
            '171',
            \Imagine\Pilotage\Numeros\TypeNumero::Regulier,
            $date('2027-01-05'),
            $date('2026-12-20'),
        );
        $calendrier = new \Imagine\Pilotage\Numeros\Calendrier([$numero]);
        $destinataire = new \Imagine\Pilotage\Envoi\Destinataire(
            'fictif',
            'Camille Fictive',
            '1 rue Imaginaire',
            '',
            '00100',
            'Ville Fictive',
            'BE',
        );
        $situation = new \Imagine\Pilotage\Envoi\Situation(
            $date('2026-11-01'),
            $date('2026-11-01'),
            'actif',
            true,
            ['171'],
            [$destinataire],
        );
        $abonnement = new \Imagine\Pilotage\Envoi\Abonnement(
            'abo-fictif',
            'abonnement',
            $date('2026-10-01'),
            [$situation],
        );
        $format = new FormatExport(['pays', 'code_postal']);
        $liste = \Imagine\Pilotage\Envoi\ListeEnvoi::etablir($numero, $calendrier, [$abonnement], $numero->cloture);
        self::assertSame("pays,code_postal\nBE,00100\n", ExportCsv::liste($liste, format: $format));
        self::assertSame('Camille Fictive', $liste->lignes[0]['destinataire']);
        $doublon = new \Imagine\Pilotage\Envoi\Abonnement(
            'abo-fictif-2',
            'abonnement',
            $date('2026-10-01'),
            [$situation],
        );
        $anormale = \Imagine\Pilotage\Envoi\ListeEnvoi::etablir(
            $numero,
            $calendrier,
            [$abonnement, $doublon],
            $numero->cloture,
        );
        self::assertSame(
            "pays,code_postal\nBE,00100\nBE,00100\n",
            ExportCsv::liste($anormale, anomaliesRevues: true, format: $format),
        );
        $this->expectException(\LogicException::class);
        ExportCsv::liste($anormale, format: $format);
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
