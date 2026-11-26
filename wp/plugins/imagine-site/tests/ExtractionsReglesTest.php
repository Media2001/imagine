<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\ExtractionsRegles;
use PHPUnit\Framework\TestCase;

final class ExtractionsReglesTest extends TestCase
{
    public function testLocaliteUsesExactCountryAndPostalCode(): void
    {
        $rows = [['pays' => 'BE', 'code_postal' => '1000'], ['pays' => 'FR', 'code_postal' => '1000'],
            ['pays' => 'BE', 'code_postal' => '10000']];
        self::assertSame([$rows[0]], ExtractionsRegles::selectionner('localite', ['pays' => 'BE', 'code_postal' => '1000'], $rows));
    }
}
