<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\ConfidentialiteRegles;
use PHPUnit\Framework\TestCase;

final class ConfidentialiteReglesTest extends TestCase
{
    public function testExportPostalNeDivulguePasLesAutresBeneficiaires(): void
    {
        $event = ['observe_utc' => '2026-11-26', 'donnees' => [
            'id' => '70', 'user' => '2', 'destinataire' => 'Payeur', 'rue' => 'Rue du payeur',
            'beneficiaires' => [['id' => '3', 'nom' => 'Cible'], ['id' => '4', 'nom' => 'Autre']],
            'relation_native' => [['user_id' => 3], ['user_id' => 4]], 'note' => 'INTERNE',
        ]];
        $out = ConfidentialiteRegles::postal($event, 3);
        self::assertStringContainsString('Cible', json_encode($out));
        foreach (['Payeur', 'Autre', 'INTERNE', 'relation_native'] as $forbidden) {
            self::assertStringNotContainsString($forbidden, json_encode($out));
        }
        self::assertNull(ConfidentialiteRegles::postal($event, 9));
    }
}
