<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\Bloc;
use Imagine\Pilotage\Acces\Moteur;
use Imagine\Pilotage\Acces\Motif;
use Imagine\Pilotage\Robots\Decision as DecisionRobot;
use Imagine\Pilotage\Robots\Motif as MotifRobot;
use PHPUnit\Framework\TestCase;

final class DecisionTest extends TestCase
{
    public static function date(string $date = '2026-11-21 12:00:00'): \DateTimeImmutable
    {
        return new \DateTimeImmutable($date, new \DateTimeZone('Europe/Brussels'));
    }

    public static function contenu(array $modifications = []): array
    {
        return array_replace([
            'reserve' => true, 'numero' => '170', 'type' => 'article',
            'sortie' => self::date('2026-10-01 00:00:00'), 'decouverte' => false,
        ], $modifications);
    }

    public static function visiteur(array $droits = [], bool $identifie = true): array
    {
        return ['identifie' => $identifie, 'droits' => $droits];
    }

    public static function robot(): DecisionRobot
    {
        return new DecisionRobot(MotifRobot::AgentInconnu);
    }

    public function testAnonymeEtIdentifieSansDroitOntDesBlocsDistincts(): void
    {
        foreach ([false, true] as $identifie) {
            $decision = (new Moteur())->decider(
                self::contenu(),
                self::visiteur([], $identifie),
                self::robot(),
                self::date(),
            );
            self::assertFalse($decision->complet);
            self::assertSame($identifie ? 'sans_droit' : 'anonyme', $decision->motif->value);
            self::assertSame($identifie ? 'abonnement' : 'connexion', $decision->bloc->value);
        }
    }

    public function testResultatRobotC03EstConsommeSansReverificationNiBooleenLibre(): void
    {
        foreach (MotifRobot::cases() as $motif) {
            $positif = in_array($motif, [MotifRobot::VerifieDns, MotifRobot::VerifiePlage], true);
            $robot = new DecisionRobot($motif, $positif ? 'google' : null);
            $decision = (new Moteur())->decider(
                self::contenu(),
                self::visiteur([], false),
                $robot,
                self::date(),
            );
            self::assertSame($positif, $decision->complet, $motif->value);
            self::assertSame($positif ? 'robot_verifie' : 'anonyme', $decision->motif->value);
        }
        foreach ([true, ['verifie' => true], new \stdClass()] as $faux) {
            $decision = (new Moteur())->decider(
                self::contenu(),
                self::visiteur([], false),
                $faux,
                self::date(),
            );
            self::assertSame(Motif::EntreeInvalide, $decision->motif);
            self::assertFalse($decision->complet);
        }
        $bing = (new Moteur())->decider(
            self::contenu(),
            self::visiteur([], false),
            new DecisionRobot(MotifRobot::VerifiePlage, 'bing'),
            self::date(),
        );
        self::assertTrue($bing->complet);
    }

    public function testFermeSansArgumentsEtOuvreUniquementUnContenuOuvertValide(): void
    {
        $moteur = new Moteur();
        $absent = $moteur->decider();
        self::assertFalse($absent->complet);
        self::assertSame(Motif::EntreeInvalide, $absent->motif);
        self::assertSame(Bloc::Abonnement, $absent->bloc);
        $ouvert = $moteur->decider(
            self::contenu(['reserve' => false]),
            self::visiteur([], false),
            self::robot(),
            self::date(),
        );
        self::assertTrue($ouvert->complet);
        self::assertSame(Motif::ContenuOuvert, $ouvert->motif);
        self::assertSame(Bloc::Aucun, $ouvert->bloc);
        self::assertSame(['complet', 'motif', 'bloc'], array_keys(get_object_vars($ouvert)));
    }
}
