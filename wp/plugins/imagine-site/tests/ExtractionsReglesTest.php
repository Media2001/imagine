<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\ExtractionsRegles;
use PHPUnit\Framework\TestCase;

final class ExtractionsReglesTest extends TestCase
{
    public function testCsvReusesC13ProtectionAndOnlyWhitelistedColumns(): void
    {
        require_once dirname(__DIR__, 2) . '/imagine-connecteur/src/CsvProtection.php';
        $row = array_fill_keys(ExtractionsRegles::COLONNES, '');
        $row['prenom'] = " \t=HYPERLINK(\"https://example.org\")";
        $row['nom'] = '+Fictif';
        $row['rue'] = 'Rue, numéro "fictif"';
        $row['note_interne'] = 'CANARI_SECRET';
        $stream = fopen('php://memory', 'w+b');
        ExtractionsRegles::csv($stream, 'localite', [$row]);
        rewind($stream);
        self::assertSame(ExtractionsRegles::COLONNES, fgetcsv($stream, escape: ''));
        $data = fgetcsv($stream, escape: '');
        self::assertSame("'" . $row['prenom'], $data[2]);
        self::assertSame("'+Fictif", $data[3]);
        self::assertSame($row['rue'], $data[6]);
        self::assertNotContains('CANARI_SECRET', $data);
        self::assertFalse(fgetcsv($stream, escape: ''));
        fclose($stream);
    }

    public static function invalidFilters(): array
    {
        return [
            ['localite', ['pays' => ['BE']]], ['localite', ['pays' => 'Belgique']],
            ['localite', ['code_postal' => "1000\n"]], ['etat', ['etat' => 'inconnu']],
            ['mode', ['mode_paiement' => '../secret']], ['echeance', ['du' => '', 'au' => '2026-12-26']],
            ['echeance', ['du' => '2026-02-30', 'au' => '2026-12-26']],
            ['echeance', ['du' => '2026-12-27', 'au' => '2026-12-26']],
            ['age', []], ['etiquette', []], ['../../secret', []],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('invalidFilters')]
    public function testInvalidFiltersFailEvenWhenThereAreNoRows(string $id, array $filters): void
    {
        $this->expectException(\InvalidArgumentException::class);
        ExtractionsRegles::selectionner($id, $filters, []);
    }

    public function testUnavailableReportsAreListedButNotExecutable(): void
    {
        $catalogue = ExtractionsRegles::catalogue();
        self::assertCount(6, $catalogue);
        self::assertFalse($catalogue['age']['disponible']);
        self::assertFalse($catalogue['etiquette']['disponible']);
    }

    public function testEtatUsesExistingLabelsWithoutChangingRights(): void
    {
        $rows = [['etat' => 'En délai de grâce'], ['etat' => 'Suspendu'], ['etat' => 'Actif']];
        self::assertSame([$rows[0]], ExtractionsRegles::selectionner('etat', ['etat' => 'En délai de grâce'], $rows));
    }

    public function testEcheanceIncludesBothDateBoundariesAndExcludesMissing(): void
    {
        $rows = [['echeance_utc' => '2026-11-26 00:00:00'], ['echeance_utc' => '2026-12-26 23:59:59'],
            ['echeance_utc' => '2026-12-27 00:00:00'], ['echeance_utc' => '']];
        self::assertSame(array_slice($rows, 0, 2), ExtractionsRegles::selectionner('echeance', ['du' => '2026-11-26', 'au' => '2026-12-26'], $rows));
    }

    public function testModeSelectsOnlyTheDeclaredPaymentMethod(): void
    {
        $rows = [['mode_paiement' => 'bacs'], ['mode_paiement' => 'imagine_papier'], ['mode_paiement' => '']];
        self::assertSame([$rows[0]], ExtractionsRegles::selectionner('mode', ['mode_paiement' => 'bacs'], $rows));
    }

    public function testLocaliteUsesExactCountryAndPostalCode(): void
    {
        $rows = [['pays' => 'BE', 'code_postal' => '1000'], ['pays' => 'FR', 'code_postal' => '1000'],
            ['pays' => 'BE', 'code_postal' => '10000']];
        self::assertSame([$rows[0]], ExtractionsRegles::selectionner('localite', ['pays' => 'BE', 'code_postal' => '1000'], $rows));
    }
}
