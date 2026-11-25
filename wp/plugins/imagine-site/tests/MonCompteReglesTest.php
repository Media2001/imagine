<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use DateTimeImmutable;
use Imagine\Site\MonCompteRegles;
use PHPUnit\Framework\TestCase;

require_once dirname(__DIR__) . '/tests-c13/bootstrap.php';
if (is_file(dirname(__DIR__) . '/MonCompteRegles.php')) {
    require_once dirname(__DIR__) . '/MonCompteRegles.php';
}

final class MonCompteReglesTest extends TestCase
{
    public function testBlocCourantPasseDe171A174Vers175A178SansFauxBlocInitial(): void
    {
        $calendar = [];
        for ($i = 0; $i < 9; $i++) {
            $sortie = (new DateTimeImmutable('2026-10-01 UTC'))->modify('+' . ($i * 3) . ' months');
            $calendar[] = ['code' => (string) (170 + $i), 'type' => 'regulier',
                'sortie' => $sortie->format('Y-m-d'), 'cloture' => $sortie->modify('-7 days')->format('Y-m-d')];
        }
        $engine = new \Imagine\Pilotage\Numeros\Moteur(\Imagine\Site\EnvoiRegles::calendrier($calendar));
        $data = ['start' => '2026-10-08 12:00:00', 'period' => 'year', 'interval' => 1];
        $first = MonCompteRegles::projeter($data, new DateTimeImmutable('2026-10-08 12:00:00 UTC'), $engine);
        self::assertSame('171', $first['premier']);
        self::assertSame('174', $first['dernier']);
        $now = new DateTimeImmutable('2027-10-08 12:00:00 UTC');
        $missing = MonCompteRegles::projeter($data, $now, $engine);
        self::assertNull($missing['premier']);
        self::assertStringContainsString('renouvellement', $missing['bloc_indisponible']);
        $data['renouvellements'] = [['id' => '20', 'debut' => '2027-10-08 12:00:00', 'paiement' => $now->getTimestamp()]];
        $renewed = MonCompteRegles::projeter($data, $now, $engine);
        self::assertSame('175', $renewed['premier']);
        self::assertSame('178', $renewed['dernier']);
        self::assertNull($renewed['bloc_indisponible']);
        $data['renouvellements'][] = $data['renouvellements'][0];
        self::assertSame($renewed, MonCompteRegles::projeter($data, $now, $engine));
        $data['renouvellements'][] = array_replace($data['renouvellements'][0], ['id' => '21']);
        self::assertNull(MonCompteRegles::projeter($data, $now, $engine)['premier']);
    }

    public function testQuatrePositionsNeDependentNiDuCalendrierNiDuDebut(): void
    {
        self::assertTrue(method_exists(MonCompteRegles::class, 'projeter'), 'La projection pure manque');
        $now = new DateTimeImmutable('2026-11-25 UTC');
        foreach (['2026-05-29 18:01:50', '', '2026-02-30 00:00:00'] as $start) {
            $view = MonCompteRegles::projeter(['period' => 'month', 'interval' => '3', 'start' => $start], $now);
            self::assertCount(4, $view['echeances']);
            self::assertSame([1, 2, 3, 4], array_column($view['echeances'], 'rang'));
            self::assertSame([null, null, null, null], array_column($view['echeances'], 'date'));
            self::assertNull($view['premier']);
        }
        self::assertSame([], MonCompteRegles::projeter(['period' => 'year', 'interval' => 1], $now)['echeances']);
        self::assertSame([], MonCompteRegles::projeter(['period' => 'month', 'interval' => 1], $now)['echeances']);
    }

    public function testEtatPurReserveVirementAuBacsEtRespecteLesBornesExactes(): void
    {
        self::assertTrue(class_exists(MonCompteRegles::class), 'Le cœur pur B02 manque');
        $now = new DateTimeImmutable('2026-11-25 20:00:00 UTC');
        foreach (['stripe' => 'Paiement en attente de validation', '' => 'Paiement en attente de validation',
            'bacs' => 'Virement en attente de validation'] as $method => $expected) {
            self::assertSame($expected, MonCompteRegles::etat(['status' => 'pending', 'method' => $method], $now));
        }
        $hold = ['status' => 'on-hold', 'method' => '', 'membership_pending' => true];
        self::assertSame('Suspendu', MonCompteRegles::etat($hold, $now));
        self::assertSame('Virement en attente de validation', MonCompteRegles::etat(array_replace($hold, ['method' => 'bacs']), $now));
        $grace = $hold + ['grace_from' => '2026-11-25 20:00:00', 'grace_until' => '2026-11-25 20:00:01'];
        self::assertSame('En délai de grâce', MonCompteRegles::etat($grace, $now));
        self::assertSame('Suspendu', MonCompteRegles::etat($grace, $now->modify('+1 second')));
        self::assertSame('Suspendu', MonCompteRegles::etat($grace, $now->modify('-1 second')));
        self::assertSame('Expiré', MonCompteRegles::etat(['status' => 'active', 'end' => '2026-11-25 20:00:00'], $now));
        self::assertSame('Actif', MonCompteRegles::etat(['status' => 'active', 'end' => '2026-11-25 20:00:01'], $now));
        self::assertSame('Expiré', MonCompteRegles::etat(['status' => 'cancelled'], $now));
        self::assertSame('Actif', MonCompteRegles::etat(['status' => 'pending-cancel'], $now));
    }
}
