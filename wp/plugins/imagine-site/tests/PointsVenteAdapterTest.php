<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\PointsVente;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class PointsVenteAdapterTest extends TestCase
{
    private array $mapping = ['nom' => 'n', 'adresse' => 'a', 'localite' => 'v', 'postal' => 'p'];
    private string $csv = "n;a;v;p\nCommerce fictif \\ A;Rue fictive;Ḉœur-Æther-Fictif;00000\n";

    protected function setUp(): void
    {
        require __DIR__ . '/PointsVenteWPStubs.php';
        require __DIR__ . '/../PointsVenteRegles.php';
        require __DIR__ . '/../PointsVente.php';
        $GLOBALS['pv_options'] = $GLOBALS['pv_posts'] = $GLOBALS['pv_meta'] = [];
        $GLOBALS['pv_reads'] = $GLOBALS['pv_deleted'] = $GLOBALS['pv_delete_fail'] = $GLOBALS['pv_translations'] = [];
        $GLOBALS['pv_next'] = 0;
    }

    public function testRepriseNonPersistableRefuseAvantBasculeEtLibereImport(): void
    {
        PointsVente::importer($this->csv, $this->mapping, ';');
        $ids = $GLOBALS['pv_options'][PointsVente::ACTIFS];
        $GLOBALS['pv_option_failure'] = PointsVente::NETTOYAGE;
        try {
            PointsVente::importer(str_replace('Commerce', 'Autre', $this->csv), $this->mapping, ';');
            self::fail('Une reprise non persistable doit refuser la bascule.');
        } catch (\RuntimeException $e) {
            self::assertSame('reprise_refusee', $e->getMessage());
        }
        self::assertSame($ids, $GLOBALS['pv_options'][PointsVente::ACTIFS]);
        self::assertArrayNotHasKey('imagine_vente_import_en_cours', $GLOBALS['pv_options']);
        self::assertSame($ids, array_keys($GLOBALS['pv_posts']));
    }

    public function testRepriseNeSupprimeNiActifNiPostEtranger(): void
    {
        PointsVente::importer($this->csv, $this->mapping, ';');
        $ids = $GLOBALS['pv_options'][PointsVente::ACTIFS];
        $GLOBALS['pv_posts'][99] = (object) ['ID' => 99, 'post_type' => 'page'];
        $GLOBALS['pv_options'][PointsVente::NETTOYAGE] = [$ids[0], 99, 100];
        $r = PointsVente::importer($this->csv, $this->mapping, ';');
        self::assertFalse($r['remplace']);
        self::assertFalse($r['nettoyage_complet']);
        self::assertSame([99], $GLOBALS['pv_options'][PointsVente::NETTOYAGE]);
        self::assertSame([], $GLOBALS['pv_deleted']);
        self::assertArrayHasKey(99, $GLOBALS['pv_posts']);
        self::assertSame($ids, $GLOBALS['pv_options'][PointsVente::ACTIFS]);
    }

    public function testEtatNettoyageDistingueBasculeEtRejeu(): void
    {
        self::assertTrue(is_callable([PointsVente::class, 'messageNettoyage']));
        self::assertSame('', PointsVente::messageNettoyage(['pris' => 1, 'refus' => []]));
        self::assertSame('Liste remplacée ; nettoyage incomplet. Recharger le même CSV pour reprendre le nettoyage.',
            PointsVente::messageNettoyage(['remplace' => true, 'nettoyage_complet' => false]));
        self::assertSame('Liste inchangée ; nettoyage incomplet. Recharger le même CSV pour reprendre le nettoyage.',
            PointsVente::messageNettoyage(['remplace' => false, 'nettoyage_complet' => false]));
    }

    public function testConfigurationLueUneSeuleFoisPourLeRendu(): void
    {
        PointsVente::importer($this->csv . "Autre fictif;Rue fictive;Ville fictive;00001\n", $this->mapping, ';');
        $GLOBALS['pv_reads'] = [];
        $html = PointsVente::afficher('');
        self::assertStringContainsString('2 points de vente', $html);
        self::assertSame(1, $GLOBALS['pv_reads'][PointsVente::CONFIG]);
    }

    public function testMotifsFrancaisTraduitsSansRecopie(): void
    {
        self::assertTrue(is_callable([PointsVente::class, 'libelleRefus']));
        foreach ([
            'nombre_colonnes' => 'Nombre de colonnes incorrect.',
            'champ_requis' => 'Champ obligatoire manquant.',
            'syntaxe_csv' => 'Syntaxe CSV incorrecte.',
            'doublon' => 'Ligne en double.',
            'champ_invalide' => 'Champ invalide.',
            'SECRET_DU_CSV' => 'Ligne refusée.',
        ] as $code => $label) {
            self::assertSame($label, PointsVente::libelleRefus($code));
            self::assertContains([$label, 'imagine-site'], $GLOBALS['pv_translations']);
        }
    }

    public function testImportRepareUneMetaActiveIllisible(): void
    {
        PointsVente::importer($this->csv, $this->mapping, ';');
        $old = $GLOBALS['pv_options'][PointsVente::ACTIFS][0];
        unset($GLOBALS['pv_meta'][$old]);
        try {
            $result = PointsVente::importer($this->csv, $this->mapping, ';');
        } catch (\RuntimeException $e) {
            self::fail('Le remplacement doit réparer la liste : ' . $e->getMessage());
        }
        self::assertSame(1, $result['pris']);
        self::assertArrayNotHasKey($old, $GLOBALS['pv_posts']);
        self::assertSame('Commerce fictif \\ A', PointsVente::lignes()[0]['nom']);
    }

    public function testSuppressionRefuseePuisRepriseIdentiqueSansChangerLesIds(): void
    {
        PointsVente::importer($this->csv, $this->mapping, ';');
        $old = $GLOBALS['pv_options'][PointsVente::ACTIFS][0];
        $GLOBALS['pv_delete_fail'] = [$old];
        $csv = str_replace('Commerce fictif', 'Autre fictif', $this->csv);
        try {
            $result = PointsVente::importer($csv, $this->mapping, ';');
        } catch (\RuntimeException $e) {
            self::fail('La liste basculée ne doit pas être annoncée refusée : ' . $e->getMessage());
        }
        $ids = $GLOBALS['pv_options'][PointsVente::ACTIFS];
        self::assertTrue($result['remplace']);
        self::assertFalse($result['nettoyage_complet']);
        self::assertSame([$old], $GLOBALS['pv_options'][PointsVente::NETTOYAGE]);
        self::assertNotSame([$old], $ids);
        self::assertArrayHasKey($old, $GLOBALS['pv_posts']);
        $GLOBALS['pv_delete_fail'] = [];
        $again = PointsVente::importer($csv, $this->mapping, ';');
        self::assertSame(['pris' => 1, 'refus' => []], $again);
        self::assertSame($ids, $GLOBALS['pv_options'][PointsVente::ACTIFS]);
        self::assertArrayNotHasKey($old, $GLOBALS['pv_posts']);
        self::assertSame([], $GLOBALS['pv_options'][PointsVente::NETTOYAGE]);
        self::assertSame('Autre fictif \\ A', PointsVente::lignes()[0]['nom']);
    }
}
