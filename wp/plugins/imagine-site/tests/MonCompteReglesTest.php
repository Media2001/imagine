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
    public function testRattachementAmbiguConserveLesAutresReglementsEtLeBlocCourant(): void
    {
        $now = new DateTimeImmutable('2027-11-25 UTC');
        $initial = ['id' => 1, 'owner' => 10, 'initial' => true, 'created' => '2026-10-08 12:00:00',
            'paid' => true, 'paid_at' => '2026-10-08 12:00:00', 'status' => 'processing', 'total' => '30.00', 'currency' => 'EUR'];
        $renewal = array_replace($initial, ['id' => 2, 'initial' => false, 'created' => '2027-10-08 12:00:00',
            'paid_at' => '2027-10-08 12:00:00', 'bloc_debut' => '2027-10-08 12:00:00']);
        $data = ['owner' => 10, 'start' => $initial['created'], 'period' => 'month', 'interval' => 3,
            'renouvellements' => [['id' => '2', 'debut' => $renewal['created'], 'paiement' => strtotime($renewal['created'] . ' UTC')]],
            'orders' => [$initial, $renewal]];
        self::assertSame(2, MonCompteRegles::projeter($data, $now)['echeances'][0]['commande']);
        $data['renouvellements'] = [];
        self::assertNull(MonCompteRegles::projeter($data, $now)['premier']);
        self::assertStringContainsString('renouvellement', MonCompteRegles::projeter($data, $now)['bloc_indisponible']);
        $data['start'] = '2027-01-01 00:00:00';
        $initial['created'] = $data['start'];
        $a = array_replace($renewal, ['id' => 3, 'created' => '2027-04-01 00:00:00', 'bloc_debut' => '']);
        $b = array_replace($a, ['id' => 4, 'total' => '45.00']);
        $last = array_replace($a, ['id' => 5, 'created' => '2027-07-01 00:00:00']);
        $data['orders'] = [$last, $b, $initial, $a];
        $view = MonCompteRegles::projeter($data, $now);
        self::assertSame('Payée', $view['echeances'][0]['etat']);
        self::assertStringContainsString('ambigu', $view['echeances'][1]['etat']);
        self::assertStringContainsString('ambigu', $view['echeances'][2]['etat']);
        self::assertSame(5, $view['echeances'][3]['commande']);
        self::assertStringContainsString('#3', implode(' ', $view['avertissements']));
        self::assertStringContainsString('#4', implode(' ', $view['avertissements']));
        self::assertStringContainsString('45.00 EUR', implode(' ', $view['avertissements']));
        $data['orders'] = [$initial, $a, array_replace($a, ['total' => '99.00']), $last];
        self::assertStringContainsString('contradictoire', implode(' ', MonCompteRegles::projeter($data, $now)['avertissements']));
    }

    public function testDeuxPaiementsNatifsDeuxFutursRejeuEtProprietaire(): void
    {
        $now = new DateTimeImmutable('2026-11-25 UTC');
        $parent = ['id' => 91, 'owner' => 10, 'initial' => true, 'created' => '2026-05-29 18:01:50',
            'paid' => true, 'paid_at' => '2026-05-29 18:01:50', 'status' => 'processing', 'total' => '30.00', 'currency' => 'EUR'];
        $renewal = array_replace($parent, ['id' => 2419, 'initial' => false,
            'created' => '2026-10-26 18:01:50', 'paid_at' => '2026-10-26 18:01:50', 'total' => '31.25']);
        $data = ['owner' => 10, 'start' => '2026-05-29 18:01:50', 'period' => 'month', 'interval' => 3,
            'total' => '30.00', 'currency' => 'EUR', 'orders' => [$renewal, $parent, $renewal]];
        $view = MonCompteRegles::projeter($data, $now);
        self::assertSame(['Payée', 'Payée', 'À venir', 'À venir'], array_column($view['echeances'], 'etat'));
        self::assertSame(['30.00', '31.25', '30.00', '30.00'], array_column($view['echeances'], 'montant'));
        self::assertSame([91, 2419, null, null], array_column($view['echeances'], 'commande'));
        $data['orders'][] = array_replace($renewal, ['id' => 999, 'owner' => 11]);
        $foreign = MonCompteRegles::projeter($data, $now);
        self::assertSame($view['echeances'], $foreign['echeances']);
        self::assertStringContainsString('propriétaire', implode(' ', $foreign['avertissements']));
        $data['orders'] = [$parent, array_replace($renewal, ['status' => 'failed', 'paid' => false, 'paid_at' => ''])];
        self::assertSame('Échouée', MonCompteRegles::projeter($data, $now)['echeances'][1]['etat']);
    }

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
