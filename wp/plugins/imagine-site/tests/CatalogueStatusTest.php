<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use PHPUnit\Framework\TestCase;

final class CatalogueStatusTest extends TestCase
{
    public function testDeliveredFunctionAloneMapsAllFourCodesAndBothDiscoveryReasons(): void
    {
        foreach ([
            [['complet' => true, 'motif' => 'contenu_ouvert'], 'libre', 'Libre'],
            [['complet' => true, 'motif' => 'decouverte_duree'], 'decouverte', 'Découverte'],
            [['complet' => true, 'motif' => 'decouverte_articles'], 'decouverte', 'Découverte'],
            [['complet' => true, 'motif' => 'numero_achete'], 'ouvert', 'Ouvert pour vous'],
            [['complet' => true, 'motif' => 'abonnement_actif'], 'ouvert', 'Ouvert pour vous'],
            [['complet' => true, 'motif' => 'motif_inconnu'], 'ouvert', 'Ouvert pour vous'],
            [['complet' => false, 'motif' => 'contenu_ouvert'], 'reserve', 'Réservé'],
            [['complet' => false, 'motif' => 'decouverte_articles'], 'reserve', 'Réservé'],
            [['complet' => false, 'motif' => 'decouverte_epuisee'], 'reserve', 'Réservé'],
            [['complet' => '1'], 'reserve', 'Réservé'], [[], 'reserve', 'Réservé'],
        ] as [$decision, $code, $label]) {
            $p = proc_open([PHP_BINARY, __DIR__ . '/b04-status-fixture.php', json_encode($decision)],
                [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']], $pipes);
            self::assertIsResource($p);
            fclose($pipes[0]);
            $out = stream_get_contents($pipes[1]);
            $err = stream_get_contents($pipes[2]);
            fclose($pipes[1]); fclose($pipes[2]);
            self::assertSame(0, proc_close($p), $err . $out);
            self::assertSame('', $err);
            $actual = json_decode($out, true, 512, JSON_THROW_ON_ERROR);
            self::assertSame(['code' => $code, 'label' => $label], $actual['status']);
            self::assertSame([], $actual['hooks'], 'Le thème livré ne doit enregistrer aucun échafaudage de démo.');
        }
    }
}
