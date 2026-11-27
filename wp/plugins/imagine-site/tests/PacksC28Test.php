<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\PacksRegles;
use PHPUnit\Framework\TestCase;

require_once dirname(__DIR__) . '/PacksRegles.php';

final class PacksC28Test extends TestCase
{
    public function testListIsStrictOrderedAndDeduplicated(): void
    {
        self::assertSame([11, 18, 25], PacksRegles::numeros(['11', 18, 11, '25']));
        self::assertSame([], PacksRegles::numeros([]));
        foreach (['11,18', null, ['011'], [11, '18junk'], [0], [-1], [true], [[11]], [11.0]] as $bad) {
            self::assertNull(PacksRegles::numeros($bad));
        }
    }

    public function testPaidEnvelopeCannotTurnMalformedDataIntoRights(): void
    {
        $snapshot = ['numeros' => [11, 18], 'paye_le' => 1234567890, 'produit' => 42];
        self::assertSame([11, 18], PacksRegles::instantane($snapshot));
        foreach ([null, [], ['numeros' => [11]], array_replace($snapshot, ['paye_le' => 0]), array_replace($snapshot, ['produit' => '42']), array_replace($snapshot, ['numeros' => [11, 'bad']])] as $bad) {
            self::assertSame([], PacksRegles::instantane($bad));
        }
    }
}
