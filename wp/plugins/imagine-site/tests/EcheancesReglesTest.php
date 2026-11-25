<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\EcheancesRegles;
use PHPUnit\Framework\TestCase;

final class EcheancesReglesTest extends TestCase
{
    public function testMandatSansReferenceResteVisibleEtExporte(): void
    {
        $row = ['id' => 1, 'etat' => 'active', 'methode' => 'imagine_papier',
            'prochaine' => 100, 'fin' => 0, 'reference' => '', 'abonne' => 'Fictif',
            'montant' => '60.00', 'devise' => 'EUR'];
        $rows = EcheancesRegles::mandats([$row], 100, 30);
        self::assertCount(1, $rows);
        self::assertSame('Référence manquante', $rows[0]['reference']);
        $stream = fopen('php://memory', 'w+');
        EcheancesRegles::csv($stream, $rows);
        rewind($stream);
        self::assertStringContainsString('Référence manquante', stream_get_contents($stream));
        fclose($stream);
    }
}
