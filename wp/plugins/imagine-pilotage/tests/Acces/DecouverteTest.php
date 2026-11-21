<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\Decouverte;
use Imagine\Pilotage\Acces\DureeDecouverte;
use Imagine\Pilotage\Acces\Moteur;
use PHPUnit\Framework\TestCase;

final class DecouverteTest extends TestCase
{
    public static function droit(array $modifications = []): array
    {
        return array_replace([
            'type' => 'decouverte', 'debut' => DecisionTest::date(),
            'compte_verifie' => true, 'consommes' => 0,
        ], $modifications);
    }

    public function testVarianteDureeReglableSansValeurParDefautEtBornesSecondes(): void
    {
        self::assertTrue(class_exists(DureeDecouverte::class));
        $reglage = new DureeDecouverte(10, ['170'], false);
        self::assertInstanceOf(Decouverte::class, $reglage);
        foreach ([-1, 0, 1, 9, 10, 11] as $secondes) {
            $instant = DecisionTest::date()->modify(sprintf('%+d seconds', $secondes));
            $decision = (new Moteur())->decider(
                DecisionTest::contenu(['decouverte' => true]),
                DecisionTest::visiteur([self::droit()]),
                DecisionTest::robot(),
                $instant,
                $reglage,
            );
            $complet = $secondes >= 0 && $secondes < 10;
            $motif = $secondes < 0 ? 'decouverte_pas_commencee'
                : ($complet ? 'decouverte_duree' : 'decouverte_epuisee');
            self::assertSame($complet, $decision->complet, (string) $secondes);
            self::assertSame($motif, $decision->motif->value);
            self::assertSame(
                $secondes >= 10 ? 'decouverte_epuisee' : ($complet ? 'aucun' : 'abonnement'),
                $decision->bloc->value,
            );
        }
    }

    public function testDureeEstEnSecondesEcouleesAuxDeuxChangementsHeure(): void
    {
        self::assertTrue(class_exists(DureeDecouverte::class));
        foreach (['2026-03-29 01:30:00', '2026-10-25 01:30:00'] as $debut) {
            $date = DecisionTest::date($debut);
            foreach ([3599, 3600, 3601] as $ecart) {
                $instant = $date->setTimestamp($date->getTimestamp() + $ecart);
                $decision = (new Moteur())->decider(
                    DecisionTest::contenu(['decouverte' => true, 'sortie' => DecisionTest::date('2026-01-01')]),
                    DecisionTest::visiteur([self::droit(['debut' => $date])]),
                    DecisionTest::robot(),
                    $instant,
                    new DureeDecouverte(3600, ['170'], false),
                );
                self::assertSame($ecart < 3600, $decision->complet, "$debut-$ecart");
            }
        }
    }

    public function testPerimetreEditorialNumerosPdfEtCompteVerifieSontExplicites(): void
    {
        self::assertTrue(class_exists(DureeDecouverte::class));
        foreach ([false, true] as $pdf) {
            foreach ([false, true] as $editorial) {
                foreach ([false, true] as $verifie) {
                    foreach (['170', '169'] as $numero) {
                        foreach (['article', 'pdf'] as $type) {
                            $decision = (new Moteur())->decider(
                                DecisionTest::contenu([
                                    'type' => $type, 'numero' => $numero, 'decouverte' => $editorial,
                                ]),
                                DecisionTest::visiteur([self::droit(['compte_verifie' => $verifie])]),
                                DecisionTest::robot(),
                                DecisionTest::date(),
                                new DureeDecouverte(10, ['170'], $pdf),
                            );
                            self::assertSame(
                                $verifie && $editorial && $numero === '170' && ($type === 'article' || $pdf),
                                $decision->complet,
                            );
                            if (!$verifie) {
                                self::assertSame('compte_non_verifie', $decision->motif->value);
                                self::assertSame('connexion', $decision->bloc->value);
                            }
                        }
                    }
                }
            }
        }
        $etendu = (new Moteur())->decider(
            DecisionTest::contenu(['decouverte' => true, 'numero' => '169']),
            DecisionTest::visiteur([self::droit()]),
            DecisionTest::robot(),
            DecisionTest::date(),
            new DureeDecouverte(20, ['169', '170'], false),
        );
        self::assertTrue($etendu->complet);
    }
}
