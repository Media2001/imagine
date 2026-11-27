<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\PointsVenteRegles;
use PHPUnit\Framework\TestCase;

require_once __DIR__ . '/../PointsVenteRegles.php';

final class PointsVenteReglesTest extends TestCase
{
    public function testRechercheExacteEtTri(): void
    {
        $rows = [
            ['nom' => 'Z fictif', 'localite' => 'Zéphyr-Fictif', 'postal' => '00002'],
            ['nom' => 'A fictif', 'localite' => 'Étoile-Fictive', 'postal' => '00001'],
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
