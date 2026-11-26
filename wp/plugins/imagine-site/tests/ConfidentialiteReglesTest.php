<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\ConfidentialiteRegles;
use PHPUnit\Framework\TestCase;

final class ConfidentialiteReglesTest extends TestCase
{
    public function testEffacementNeModifiePasUneObservationEtrangereDuGel(): void
    {
        $foreign = ['donnees' => ['id' => '70', 'user' => '2', 'beneficiaires_resolus' => true]];
        self::assertSame($foreign, ConfidentialiteRegles::retirerPostal($foreign, 3));
        self::assertNull(ConfidentialiteRegles::retirerPostal($foreign, 2));
        $shared = ['donnees' => ['user' => '2', 'beneficiaires' => [['id' => '3'], ['id' => '4']],
            'relation_native' => [['user_id' => 3], ['user_id' => 4]], 'beneficiaires_resolus' => true]];
        $out = ConfidentialiteRegles::retirerPostal($shared, 3);
        self::assertSame([['id' => '4']], $out['donnees']['beneficiaires']);
        self::assertSame([['user_id' => 4]], $out['donnees']['relation_native']);
        self::assertFalse($out['donnees']['beneficiaires_resolus']);
    }

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
