<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\{ExtractionsAdmin, ExtractionsNatives, ExtractionsRegles, MonCompte, TableauBordRegles};
use PHPUnit\Framework\Attributes\{DataProvider, PreserveGlobalState, RunTestsInSeparateProcesses};
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class ExtractionsNativesTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/fixtures/c18-faux-natif.php';
        $GLOBALS['c18_queries'] = [];
        $GLOBALS['c18_pages'] = [];
        $GLOBALS['c18_translate'] = false;
    }

    public function testTranslatedDisplayDoesNotChangeNativeSelectionOrC19Totals(): void
    {
        $active = new \WC_Subscription(101, 'active');
        $GLOBALS['c18_pages'] = [1 => [$active, new \WC_Subscription(102)]];
        $before = ExtractionsNatives::lire('etat', ['etat' => 'Actif']);
        $GLOBALS['c18_translate'] = true;
        self::assertSame('Active', MonCompte::etat($active));
        $after = ExtractionsNatives::lire('etat', ['etat' => 'Actif']);
        self::assertSame(['101'], array_column($before, 'abonnement_id'));
        self::assertSame($before, $after, 'Le même filtre doit garder les mêmes identifiants sous traduction.');
        self::assertSame('Actif', $after[0]['etat'], 'Contrat stable consommé par C19.');
        self::assertSame(ExtractionsRegles::COLONNES, array_keys($after[0]));
        self::assertSame('Active', ExtractionsAdmin::affichage($after)[0]['etat']);
        $metric = TableauBordRegles::calculer('actifs', ['abonnements' => $after]);
        self::assertSame(['total' => 1, 'mode:bacs' => 1], $metric['valeurs']);
        self::assertSame('Actif', ExtractionsRegles::filtres('etat', ['etat' => 'Actif'])['etat']);
    }

    public static function sizes(): array
    {
        return [[100, [100, 0], []], [101, [100, 1], ['101']]];
    }

    #[DataProvider('sizes')]
    public function testNativePaginationReachesSecondPageAndStops(int $size, array $counts, array $expected): void
    {
        $all = [];
        for ($id = 1; $id <= $size; $id++) {
            $all[] = new \WC_Subscription($id, $id === 101 ? 'active' : 'on-hold');
        }
        $GLOBALS['c18_pages'] = [1 => array_slice($all, 0, 100), 2 => array_slice($all, 100)];
        $selected = ExtractionsNatives::lire('etat', ['etat' => 'Actif']);
        self::assertSame($expected, array_column($selected, 'abonnement_id'));
        self::assertSame([1, 2], array_column($GLOBALS['c18_queries'], 'paged'));
        self::assertSame([100, 100], array_column($GLOBALS['c18_queries'], 'subscriptions_per_page'));
        self::assertSame($counts, array_values(array_map('count', $GLOBALS['c18_pages'])));
        $GLOBALS['c18_queries'] = [];
        $rows = ExtractionsNatives::lire('localite', []);
        $ids = array_column($rows, 'abonnement_id');
        self::assertCount($size, $rows);
        self::assertSame($ids, array_values(array_unique($ids)));
        self::assertSame(array_map('strval', range(1, $size)), $ids);
        self::assertSame([1, 2], array_column($GLOBALS['c18_queries'], 'paged'));
    }

    public function testNativeBoundaryOverlapDoesNotDuplicateSubscription(): void
    {
        $GLOBALS['c18_pages'][1] = array_map(static fn (int $id) => new \WC_Subscription($id), range(1, 100));
        $GLOBALS['c18_pages'][2] = [new \WC_Subscription(100), new \WC_Subscription(101, 'active')];
        $rows = ExtractionsNatives::lire('localite', []);
        self::assertCount(101, $rows);
        self::assertSame(array_map('strval', range(1, 101)), array_column($rows, 'abonnement_id'));
        self::assertSame([1, 2], array_column($GLOBALS['c18_queries'], 'paged'));
    }
}
