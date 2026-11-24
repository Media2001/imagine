<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use PHPUnit\Framework\TestCase;

final class DecouverteTest extends TestCase
{
    private function request(array $steps, string $relecture = 'fermee'): array
    {
        $process = proc_open([PHP_BINARY, __DIR__ . '/fixture.php', json_encode(compact('steps', 'relecture'), JSON_THROW_ON_ERROR)],
            [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']], $pipes);
        self::assertIsResource($process);
        fclose($pipes[0]);
        $out = stream_get_contents($pipes[1]);
        $err = stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        self::assertSame(0, proc_close($process), $err . $out);
        self::assertSame('', $err);
        return json_decode($out, true, 512, JSON_THROW_ON_ERROR);
    }

    public function testRelecturePolicyIsExplicitAndNeverRecredits(): void
    {
        $rows = $this->request([
            ['article' => 'un'], ['article' => 'un'], ['article' => 'deux'],
            ['article' => 'un'], ['article' => 'un', 'setting' => 'rester_lisible'],
            ['article' => 'trois'], ['article' => 'non'],
            ['article' => 'un', 'scope' => []],
        ]);
        self::assertSame($rows[0]['state'], $rows[1]['state']);
        self::assertTrue($rows[2]['decision']['complet']);
        self::assertFalse($rows[3]['decision']['complet']);
        self::assertSame('decouverte_epuisee', $rows[3]['decision']['motif']);
        self::assertTrue($rows[4]['decision']['complet']);
        self::assertSame($rows[3]['state'], $rows[4]['state']);
        self::assertFalse($rows[5]['decision']['complet']);
        self::assertFalse($rows[6]['decision']['complet']);
        self::assertFalse($rows[7]['decision']['complet']);
        self::assertSame($rows[3]['state'], $rows[7]['state']);
    }

    public function testOnlyDesignatedArticleOfSameIssueCanOpenAndConsume(): void
    {
        $rows = $this->request([['article' => 'non'], ['article' => 'un'], ['article' => 'non']]);
        self::assertFalse($rows[0]['decision']['complet']);
        self::assertNull($rows[0]['state']);
        self::assertTrue($rows[1]['decision']['complet']);
        self::assertSame([101], $rows[1]['state']['articles']);
        self::assertFalse($rows[2]['decision']['complet']);
        self::assertSame($rows[1]['state'], $rows[2]['state']);
    }

    public function testInvalidOrRevokedDesignationNeverGrantsRelecture(): void
    {
        $rows = $this->request([
            ['article' => 'non', 'marker' => false], ['article' => 'non', 'marker' => 'yes'],
            ['article' => 'un'], ['article' => 'un', 'marker' => false],
        ], 'rester_lisible');
        self::assertNull($rows[0]['state']);
        self::assertNull($rows[1]['state']);
        self::assertTrue($rows[2]['decision']['complet']);
        self::assertFalse($rows[3]['decision']['complet']);
        self::assertSame($rows[2]['state'], $rows[3]['state']);
    }

    public function testFutureWithNoStateAndAvailableQuotaIsNonConsuming(): void
    {
        $rows = $this->request([
            ['article' => 'trois', 'future' => true], ['article' => 'un'],
            ['article' => 'trois', 'future' => true],
        ]);
        self::assertSame('contenu_futur_ferme_par_reglage', $rows[0]['decision']['motif']);
        self::assertFalse($rows[0]['decision']['complet']);
        self::assertNull($rows[0]['state']);
        self::assertSame('contenu_futur_ferme_par_reglage', $rows[2]['decision']['motif']);
        self::assertFalse($rows[2]['decision']['complet']);
        self::assertSame($rows[1]['state'], $rows[2]['state']);
        self::assertSame([101], $rows[2]['state']['articles']);
    }

    public function testNonReadingAndNewSessionCannotResetAccount(): void
    {
        $rows = $this->request([
            ['article' => 'un', 'reading' => false], ['article' => 'un'],
            ['article' => 'un', 'reading' => false], ['article' => 'deux'],
            ['article' => 'trois'], ['article' => 'un', 'setting' => 'unknown'],
        ]);
        self::assertFalse($rows[0]['decision']['complet']);
        self::assertNull($rows[0]['state']);
        self::assertFalse($rows[2]['decision']['complet']);
        self::assertSame($rows[1]['state'], $rows[2]['state']);
        self::assertFalse($rows[4]['decision']['complet']);
        self::assertFalse($rows[5]['decision']['complet']);
        self::assertSame($rows[3]['state'], $rows[5]['state']);
    }

    public function testCurrentScopeCannotExpandFrozenScope(): void
    {
        $rows = $this->request([
            ['article' => 'un', 'scope' => ['39']],
            ['article' => 'deux', 'scope' => ['39', '25']],
        ]);
        self::assertTrue($rows[0]['decision']['complet']);
        self::assertFalse($rows[1]['decision']['complet']);
        self::assertSame($rows[0]['state'], $rows[1]['state']);
    }

    public function testMissingVerificationAndFailedPersistenceDoNotOpen(): void
    {
        $rows = $this->request([
            ['article' => 'un', 'verified' => ''],
            ['article' => 'un', 'verified' => '1', 'deny_write' => true],
        ]);
        self::assertFalse($rows[0]['decision']['complet']);
        self::assertNull($rows[0]['state']);
        self::assertFalse($rows[1]['decision']['complet']);
        self::assertNull($rows[1]['state']);
    }
}
