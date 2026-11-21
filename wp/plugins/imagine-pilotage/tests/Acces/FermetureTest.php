<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\Decouverte;
use Imagine\Pilotage\Acces\DureeDecouverte;
use Imagine\Pilotage\Acces\Moteur;
use Imagine\Pilotage\Acces\Motif;
use Imagine\Pilotage\Acces\NombreArticlesDecouverte;
use Imagine\Pilotage\Robots\Decision as DecisionRobot;
use Imagine\Pilotage\Robots\Motif as MotifRobot;
use PHPUnit\Framework\TestCase;

final class FermetureTest extends TestCase
{
    private function ferme(array $arguments): void
    {
        $decision = (new Moteur())->decider(...$arguments);
        self::assertFalse($decision->complet);
        self::assertSame('entree_invalide', $decision->motif->value);
        self::assertSame('abonnement', $decision->bloc->value);
    }

    public function testChaqueChampAbsentInconnuOuMalTypeFermeMemeOuvertEquipeEtRobot(): void
    {
        $valeurs = [null, false, true, 0, 1, '', 'inconnu', [], new \stdClass()];
        $base = [
            DecisionTest::contenu(['reserve' => false]),
            DecisionTest::visiteur([['type' => 'equipe', 'role' => 'administration']]),
            new DecisionRobot(MotifRobot::VerifieDns, 'google'),
            DecisionTest::date(),
        ];
        foreach ([0, 1, 2, 3] as $index) {
            foreach ($valeurs as $valeur) {
                $arguments = $base;
                $arguments[$index] = $valeur;
                $this->ferme($arguments);
            }
        }
        foreach ([0, 1] as $index) {
            foreach (array_keys($base[$index]) as $cle) {
                $arguments = $base;
                unset($arguments[$index][$cle]);
                $this->ferme($arguments);
            }
            $arguments = $base;
            $arguments[$index]['inconnu'] = true;
            $this->ferme($arguments);
        }
        foreach (['reserve', 'numero', 'type', 'sortie', 'decouverte'] as $cle) {
            foreach ($valeurs as $valeur) {
                if (
                    (($cle === 'reserve' || $cle === 'decouverte') && is_bool($valeur))
                    || ($cle === 'numero' && $valeur === 'inconnu')
                ) {
                    continue;
                }
                $arguments = $base;
                $arguments[0][$cle] = $valeur;
                $this->ferme($arguments);
            }
        }
        foreach (['identifie', 'droits'] as $cle) {
            foreach ($valeurs as $valeur) {
                if (($cle === 'identifie' && $valeur === true) || ($cle === 'droits' && $valeur === [])) {
                    continue;
                }
                $arguments = $base;
                $arguments[1][$cle] = $valeur;
                $this->ferme($arguments);
            }
        }
    }

    public function testDroitMalformedOuInconnuNeSeCachePasDerriereUnDroitValide(): void
    {
        $exemples = [
            AbonnementTest::droit(), DroitsTest::achat(), DecouverteTest::droit(),
            ['type' => 'equipe', 'role' => 'redaction'], ['type' => 'cooperateur'],
        ];
        foreach ($exemples as $droit) {
            $invalides = [];
            foreach (array_keys($droit) as $cle) {
                $absent = $droit;
                unset($absent[$cle]);
                $invalides[] = $absent;
                $invalides[] = array_replace($droit, [$cle => new \stdClass()]);
            }
            $invalides[] = $droit + ['inconnu' => 1];
            foreach ($invalides as $invalide) {
                foreach ([[$invalide, DroitsTest::achat()], [DroitsTest::achat(), $invalide]] as $droits) {
                    $this->ferme([
                        DecisionTest::contenu(['reserve' => false]),
                        DecisionTest::visiteur($droits),
                        new DecisionRobot(MotifRobot::VerifiePlage, 'bing'),
                        DecisionTest::date(),
                        new DureeDecouverte(10, ['170'], false),
                    ]);
                }
            }
        }
        $invalides = [
            null, false, 'actif', [], ['type' => 'inconnu'],
            ['type' => 'equipe', 'role' => 'cooperateur'],
            AbonnementTest::droit(['fin' => DecisionTest::date('2026-10-01')]),
            AbonnementTest::droit(['fin' => DecisionTest::date('2026-09-01')]),
            AbonnementTest::droit(['etat' => 'on-hold']),
            DroitsTest::achat(' 170'), DroitsTest::achat('170 '),
            DecouverteTest::droit(['consommes' => -1]),
            DecouverteTest::droit(['consommes' => 1.0]),
            DecouverteTest::droit(['compte_verifie' => 1]),
        ];
        foreach ($invalides as $droit) {
            $this->ferme([
                DecisionTest::contenu(), DecisionTest::visiteur([$droit]),
                DecisionTest::robot(), DecisionTest::date(), new DureeDecouverte(10, ['170'], false),
            ]);
        }
        $this->ferme([
            DecisionTest::contenu(), DecisionTest::visiteur([DroitsTest::achat()], false),
            DecisionTest::robot(), DecisionTest::date(),
        ]);
        $this->ferme([
            DecisionTest::contenu(), ['identifie' => true, 'droits' => ['x' => DroitsTest::achat()]],
            DecisionTest::robot(), DecisionTest::date(),
        ]);
    }

    public function testConfigurationDecouverteInvalideAbsenteOuVarianteInconnueFerme(): void
    {
        $inconnue = new class implements Decouverte {
            public function estValide(): bool
            {
                throw new \RuntimeException('Ne jamais autoriser sur exception.');
            }

            public function evaluer(array $contenu, array $droit, \DateTimeImmutable $instant): Motif
            {
                return Motif::DecouverteDuree;
            }
        };
        $reglages = [null, true, [], new \stdClass(), $inconnue];
        foreach ([DureeDecouverte::class, NombreArticlesDecouverte::class] as $classe) {
            foreach ([0, -1, 1.0, '1', true, null, []] as $valeur) {
                $reglages[] = new $classe($valeur, ['170'], false);
            }
            foreach ([null, false, '170', [170], [''], [' 170'], ['170 '], ['170', '170'], ['x' => '170']] as $scope) {
                $reglages[] = new $classe(10, $scope, false);
            }
            foreach ([null, 0, 1, 'false'] as $pdf) {
                $reglages[] = new $classe(10, ['170'], $pdf);
            }
        }
        foreach ($reglages as $reglage) {
            $this->ferme([
                DecisionTest::contenu(), DecisionTest::visiteur([DecouverteTest::droit(), DroitsTest::achat()]),
                DecisionTest::robot(), DecisionTest::date(), $reglage,
            ]);
        }
        $this->ferme([
            DecisionTest::contenu(), DecisionTest::visiteur([DecouverteTest::droit(), DecouverteTest::droit()]),
            DecisionTest::robot(), DecisionTest::date(), new DureeDecouverte(10, ['170'], false),
        ]);
    }

    public function testDateFractionnaireFutureEtRobotInconnuFerment(): void
    {
        foreach ([' 170', '170 ', "170\n"] as $numero) {
            $this->ferme([
                DecisionTest::contenu(['numero' => $numero]), DecisionTest::visiteur(),
                DecisionTest::robot(), DecisionTest::date(),
            ]);
        }
        $this->ferme([
            DecisionTest::contenu(), DecisionTest::visiteur(),
            new DecisionRobot(MotifRobot::VerifieDns, 'robot_inconnu'), DecisionTest::date(),
        ]);
        $this->ferme([
            DecisionTest::contenu(['sortie' => DecisionTest::date('2026-11-21 12:00:01')]),
            DecisionTest::visiteur([DroitsTest::achat()]), DecisionTest::robot(), DecisionTest::date(),
        ]);
        $fraction = DecisionTest::date('2026-11-21 12:00:00.500000');
        $this->ferme([
            DecisionTest::contenu(), DecisionTest::visiteur([DroitsTest::achat()]), DecisionTest::robot(), $fraction,
        ]);
        foreach (
            [
            AbonnementTest::droit(['debut' => $fraction]),
            DroitsTest::achat() + ['inconnu' => true],
            array_replace(DroitsTest::achat(), ['acquis_le' => $fraction]),
            DecouverteTest::droit(['debut' => $fraction]),
            ] as $droit
        ) {
            $this->ferme([
                DecisionTest::contenu(), DecisionTest::visiteur([$droit]), DecisionTest::robot(),
                DecisionTest::date(), new DureeDecouverte(10, ['170'], false),
            ]);
        }
    }

    public function testExceptionDateInjecteeEstFermeeSansEchapper(): void
    {
        $date = new class ('2026-11-21 12:00:00', new \DateTimeZone('Europe/Brussels')) extends \DateTimeImmutable {
            public function getTimestamp(): int
            {
                throw new \RuntimeException('Date indisponible');
            }
        };
        $this->ferme([
            DecisionTest::contenu(['decouverte' => true]), DecisionTest::visiteur([DecouverteTest::droit()]),
            DecisionTest::robot(), $date, new DureeDecouverte(10, ['170'], false),
        ]);
    }
}
