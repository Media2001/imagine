<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Acquisition;
use Imagine\Site\AcquisitionConfidentialite;
use Imagine\Site\AcquisitionReglages;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class AcquisitionAdapterTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/AcquisitionWPStubs.php';
        $GLOBALS['c27_options'] = [Acquisition::OPTION => ['lune' => 'Radio fictive \\ lune', 'mars' => 'Journal fictif']];
        $GLOBALS['c27_meta'] = [];
        $GLOBALS['c27_orders'] = [1 => new \WC_Order(), 2 => new \WC_Order(), 3 => new \WC_Order(owner: 29)];
        $GLOBALS['c27_user_sql_fail'] = false;
        $GLOBALS['wpdb'] = new class {
            public string $last_error = '';
            public string $prefix = 'fictif_';
            public string $options = 'fictif_options';
            public bool $fail = false;
            private ?array $transaction = null;
            public function prepare(string $query, mixed ...$args): array { return [$query, $args]; }
            public function esc_like(string $value): string { return addcslashes($value, '_%\\'); }
            public function get_var(mixed $query): int { return 1; }
            public function query(string $query): bool
            {
                if ($query === 'START TRANSACTION') { $this->transaction = [$GLOBALS['c27_options'], $GLOBALS['c27_meta']]; }
                if ($query === 'ROLLBACK' && $this->transaction !== null) { [$GLOBALS['c27_options'], $GLOBALS['c27_meta']] = $this->transaction; }
                if (in_array($query, ['COMMIT', 'ROLLBACK'], true)) { $this->transaction = null; }
                return true;
            }
            public function get_results(array $query, mixed $format): ?array
            {
                if ($this->fail) { $this->last_error = 'lecture fictive refusée'; return null; }
                $this->last_error = '';
                $prefix = stripslashes(substr($query[1][0], 0, -1));
                $rows = [];
                foreach ($GLOBALS['c27_options'] as $key => $value) {
                    if (str_starts_with($key, $prefix)) { $rows[] = ['option_name' => $key, 'option_value' => serialize($value)]; }
                }
                return $rows;
            }
        };
        if (!defined('ARRAY_A')) { define('ARRAY_A', 'ARRAY_A'); }
    }

    public function testReponseUniqueTiersEtC16FermesSourceNonEcrasee(): void
    {
        self::assertTrue(Acquisition::repondre(1, 28, 'lune'));
        $first = $GLOBALS['c27_options'][Acquisition::REPONSE . '1'];
        self::assertSame('Radio fictive \\ lune', $first['libelle']);
        self::assertSame($first, $GLOBALS['c27_meta'][28][Acquisition::SOURCE]);
        self::assertInstanceOf(\WP_Error::class, Acquisition::repondre(1, 28, 'mars'));
        self::assertSame($first, $GLOBALS['c27_options'][Acquisition::REPONSE . '1']);
        self::assertInstanceOf(\WP_Error::class, Acquisition::repondre(2, 29, 'lune'));
        self::assertTrue(Acquisition::repondre(2, 28, 'mars'));
        self::assertSame($first, $GLOBALS['c27_meta'][28][Acquisition::SOURCE]);
        $GLOBALS['c27_orders'][4] = new \WC_Order(via: 'imagine-c16');
        self::assertInstanceOf(\WP_Error::class, Acquisition::repondre(4, 28, 'lune'));
        self::assertArrayNotHasKey(Acquisition::REPONSE . '4', $GLOBALS['c27_options']);
    }

    public function testAucuneTraceAvantPaiementNiListeVide(): void
    {
        $GLOBALS['c27_orders'][1]->paid = false;
        $GLOBALS['c27_orders'][1]->dated = false;
        $before = $GLOBALS['c27_options'];
        self::assertInstanceOf(\WP_Error::class, Acquisition::repondre(1, 28, 'lune'));
        self::assertSame($before, $GLOBALS['c27_options']);
        self::assertSame([], $GLOBALS['c27_meta']);
        $GLOBALS['c27_options'][Acquisition::OPTION] = [];
        self::assertInstanceOf(\WP_Error::class, Acquisition::repondre(2, 28, 'lune'));
        self::assertArrayNotHasKey(Acquisition::REPONSE . '2', $GLOBALS['c27_options']);
    }

    public function testReglageFermeVideDupliqueEtAntislash(): void
    {
        self::assertSame(['lune' => 'Radio fictive \\ lune'], AcquisitionReglages::nettoyer('lune|Radio fictive \\ lune'));
        self::assertSame([], AcquisitionReglages::nettoyer(''));
        self::assertSame(Acquisition::configuration(), AcquisitionReglages::nettoyer("lune|Un\nlune|Deux"));
        self::assertSame(Acquisition::configuration(), AcquisitionReglages::nettoyer('bad key|Un'));
    }

    public function testExportEffacementEtTiersPreservePagination(): void
    {
        Acquisition::repondre(1, 28, 'lune');
        Acquisition::repondre(3, 29, 'mars');
        $third = $GLOBALS['c27_options'][Acquisition::REPONSE . '3'];
        $export = AcquisitionConfidentialite::exporter('lecteur@example.org');
        self::assertCount(2, $export['data']);
        self::assertTrue($export['done']);
        self::assertSame('Radio fictive \\ lune', $export['data'][0]['data'][2]['value']);
        self::assertSame(['data' => [], 'done' => true], AcquisitionConfidentialite::exporter('lecteur@example.org', 2));
        $erase = AcquisitionConfidentialite::effacer('lecteur@example.org');
        self::assertTrue($erase['items_removed']);
        self::assertFalse($erase['items_retained']);
        self::assertTrue($erase['done']);
        self::assertSame(['commande' => 1, 'etat' => 'effacee'], $GLOBALS['c27_options'][Acquisition::REPONSE . '1']);
        self::assertSame($third, $GLOBALS['c27_options'][Acquisition::REPONSE . '3']);
        self::assertSame(['data' => [], 'done' => true], AcquisitionConfidentialite::exporter('lecteur@example.org'));
        self::assertInstanceOf(\WP_Error::class, Acquisition::repondre(1, 28, 'mars'));
    }

    public function testPanneLectureNeDevientJamaisUnExportVideNiUnEffacementReussi(): void
    {
        Acquisition::repondre(1, 28, 'lune');
        $before = $GLOBALS['c27_options'];
        $GLOBALS['wpdb']->fail = true;
        self::assertInstanceOf(\WP_Error::class, AcquisitionConfidentialite::exporter('lecteur@example.org'));
        $erase = AcquisitionConfidentialite::effacer('lecteur@example.org');
        self::assertTrue($erase['items_retained']);
        self::assertFalse($erase['done']);
        self::assertSame($before, $GLOBALS['c27_options']);
        $GLOBALS['wpdb']->fail = false;
        $GLOBALS['c27_user_sql_fail'] = true;
        self::assertInstanceOf(\WP_Error::class, AcquisitionConfidentialite::exporter('lecteur@example.org'));
        self::assertTrue(AcquisitionConfidentialite::effacer('lecteur@example.org')['items_retained']);
    }
}
