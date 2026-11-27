<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\PointsVenteRegles;
use PHPUnit\Framework\TestCase;

require_once __DIR__ . '/../PointsVenteRegles.php';

final class PointsVenteReglesTest extends TestCase
{
    public function testColonnesOptionnellesEtCsvStandard(): void
    {
        $map = ['nom' => 'n', 'adresse' => 'a', 'localite' => 'v', 'postal' => 'p', 'personne' => 'contact', 'telephone' => 'tel'];
        $csv = "\xEF\xBB\xBFn,a,v,p,contact,tel\r\n\"Kiosque, fictif\",\"Rue \"\"inventée\"\"\",Étoile,00001,Personnage fictif,000-fictif\r\n";
        $r = PointsVenteRegles::charger($csv, $map, ',');
        self::assertSame('Kiosque, fictif', $r['lignes'][0]['nom']);
        self::assertSame('Rue "inventée"', $r['lignes'][0]['adresse']);
        self::assertSame('Personnage fictif', $r['lignes'][0]['personne']);
        self::assertSame('000-fictif', $r['lignes'][0]['telephone']);
        $multi = "n;a;v;p\n\"Nom\nfictif\";rue;ville;00001\nmal;forme\n";
        $r = PointsVenteRegles::charger($multi, array_slice($map, 0, 4), ';');
        self::assertSame([['ligne' => 4, 'motif' => 'nombre_colonnes']], $r['refus']);
    }

    public function testRefusSansDonneeEtDoublon(): void
    {
        $map = ['nom' => 'n', 'adresse' => 'a', 'localite' => 'v', 'postal' => 'p'];
        $csv = "n;a;v;p\nFictif;rue;Étoile;00001\nFictif;rue;Étoile;00001\n;RUE_SECRETE;ville;00001\n\"guillemet\"suffixe;rue;ville;00001\n";
        $r = PointsVenteRegles::charger($csv, $map, ';');
        self::assertCount(1, $r['lignes']);
        self::assertSame([
            ['ligne' => 3, 'motif' => 'doublon'],
            ['ligne' => 4, 'motif' => 'champ_requis'],
            ['ligne' => 5, 'motif' => 'syntaxe_csv'],
        ], $r['refus']);
        self::assertStringNotContainsString('RUE_SECRETE', json_encode($r));
    }

    public function testFichiersEtMappingsInvalides(): void
    {
        $map = ['nom' => 'n', 'adresse' => 'a', 'localite' => 'v', 'postal' => 'p'];
        foreach ([
            ['', $map, ';'],
            ["n;a;v;p\n;rue;ville;00001\n", $map, ';'],
            ["n;n;v;p\nA;B;V;P\n", $map, ';'],
            ["n;a;v;p\nA;B;V;P\n", ['nom' => 'n'], ';'],
            ["n;a;v;p\nA;B;V;P\n", $map + ['secret' => 'n'], ';'],
            ["n;a;v;p\nA;B;V;P\n", $map, '|'],
            ["n;a;v;p\nA;\xFF;V;P\n", $map, ';'],
        ] as [$csv, $mapping, $delimiter]) {
            try {
                PointsVenteRegles::charger($csv, $mapping, $delimiter);
                self::fail('Fichier invalide accepté');
            } catch (\InvalidArgumentException $e) {
                self::assertMatchesRegularExpression('/^[a-z_]+$/', $e->getMessage());
            }
        }
    }

    public function testRechercheExacteEtTri(): void
    {
        $rows = [
            ['nom' => 'Z fictif', 'adresse' => '2 rue fictive', 'localite' => 'Zéphyr-Fictif', 'postal' => '00002'],
            ['nom' => 'A fictif', 'adresse' => '1 rue fictive', 'localite' => 'Étoile-Fictive', 'postal' => '00001'],
        ];
        self::assertSame([$rows[1]], PointsVenteRegles::rechercher($rows, 'ETOILE-FICTIVE'));
        self::assertSame([$rows[1]], PointsVenteRegles::rechercher($rows, 'étoile-fictive'));
        self::assertSame([$rows[1]], PointsVenteRegles::rechercher($rows, '00001'));
        self::assertSame([], PointsVenteRegles::rechercher($rows, '000'));
        self::assertSame([], PointsVenteRegles::rechercher($rows, 'fictif'));
        self::assertSame([$rows[1], $rows[0]], PointsVenteRegles::rechercher($rows, ''));
    }

    public function testCsvMappingProjectionEtRefus(): void
    {
        $csv = "enseigne;rue;ville;cp;personne;tel\nFictif \\ kiosque;1 rue inventée;Étoile-Fictive;00001;SECRET;123\nMalformé;incomplet\n";
        $result = PointsVenteRegles::charger($csv, ['nom' => 'enseigne', 'adresse' => 'rue', 'localite' => 'ville', 'postal' => 'cp'], ';');
        self::assertCount(1, $result['lignes']);
        self::assertSame('Fictif \\ kiosque', $result['lignes'][0]['nom']);
        self::assertSame(['ligne' => 3, 'motif' => 'nombre_colonnes'], $result['refus'][0]);
        self::assertArrayNotHasKey('personne', $result['lignes'][0]);
        self::assertStringNotContainsString('SECRET', json_encode($result));
    }
}
