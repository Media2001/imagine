<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use PHPUnit\Framework\TestCase;

final class CatalogueTest extends TestCase
{
    private function request(array $steps): array
    {
        $p = proc_open([PHP_BINARY, __DIR__ . '/b04-adapter-fixture.php', json_encode(['steps' => $steps], JSON_THROW_ON_ERROR)],
            [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']], $pipes);
        self::assertIsResource($p);
        fclose($pipes[0]);
        $out = stream_get_contents($pipes[1]);
        $err = stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        self::assertSame(0, proc_close($p), $err . $out);
        self::assertSame('', $err);
        return json_decode($out, true, 512, JSON_THROW_ON_ERROR);
    }

    public function testOwnershipDoesNotBecomeAnotherPurchaseBeforeRelease(): void
    {
        $rows = $this->request([
            ['issue' => true, 'purchased' => true, 'instant' => '2098-12-31 23:59:59 UTC'],
            ['issue' => true, 'instant' => '2099-01-01 00:00:00 UTC'],
            ['issue' => true, 'purchased' => false],
        ]);
        self::assertTrue($rows[0]['possede']);
        self::assertFalse($rows[0]['pdf']['complet']);
        self::assertSame('contenu_futur_ferme_par_reglage', $rows[0]['pdf']['motif']);
        self::assertTrue($rows[1]['possede']);
        self::assertTrue($rows[1]['pdf']['complet']);
        self::assertFalse($rows[2]['possede']);
        self::assertFalse($rows[2]['pdf']['complet']);
    }

    public function testListingPredictsFirstReadWithoutOpeningOrConsuming(): void
    {
        $rows = $this->request([
            ['article' => 'un', 'reading' => false, 'listing' => true],
            ['article' => 'un', 'reading' => false], ['article' => 'un'],
            ['article' => 'deux', 'reading' => false, 'listing' => true], ['article' => 'deux'],
            ['article' => 'trois', 'reading' => false, 'listing' => true],
        ]);
        self::assertSame('decouverte_articles', $rows[0]['decision']['motif']);
        self::assertTrue($rows[0]['decision']['complet']);
        self::assertNull($rows[0]['state']);
        self::assertFalse($rows[1]['decision']['complet']);
        self::assertNull($rows[1]['state']);
        self::assertSame([101], $rows[2]['state']['articles']);
        self::assertTrue($rows[3]['decision']['complet']);
        self::assertSame($rows[2]['state'], $rows[3]['state']);
        self::assertSame([101, 103], $rows[4]['state']['articles']);
        self::assertFalse($rows[5]['decision']['complet']);
        self::assertSame($rows[4]['state'], $rows[5]['state']);
    }

    public function testListingUsesDurationAndClosesInvalidVerificationDesignationAndFuture(): void
    {
        $rows = $this->request([
            ['article' => 'un', 'reading' => false, 'listing' => true, 'verified' => ''],
            ['article' => 'non', 'reading' => false, 'listing' => true, 'verified' => '1'],
            ['article' => 'un', 'reading' => false, 'listing' => true, 'form' => 'duree'],
            ['article' => 'trois', 'reading' => false, 'listing' => true, 'future' => true],
        ]);
        self::assertFalse($rows[0]['decision']['complet']);
        self::assertFalse($rows[1]['decision']['complet']);
        self::assertSame('decouverte_duree', $rows[2]['decision']['motif']);
        self::assertTrue($rows[2]['decision']['complet']);
        self::assertFalse($rows[3]['decision']['complet']);
        foreach ($rows as $row) { self::assertNull($row['state']); }
    }
}
