<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\Decouverte;
use Imagine\Pilotage\Acces\DureeDecouverte;
use Imagine\Pilotage\Acces\Moteur;
use Imagine\Pilotage\Acces\NombreArticlesDecouverte;
use PHPUnit\Framework\TestCase;

final class QuotaTest extends TestCase
{
    public function testVarianteNombreArticlesReglableCompteInstantaneSansConsommer(): void
    {
        self::assertTrue(class_exists(NombreArticlesDecouverte::class));
        foreach ([1, 3] as $quota) {
            $reglage = new NombreArticlesDecouverte($quota, ['170'], false);
            self::assertInstanceOf(Decouverte::class, $reglage);
            foreach ([0, $quota - 1, $quota, $quota + 1] as $consommes) {
                $droit = DecouverteTest::droit(['consommes' => $consommes]);
                $avant = $droit;
                foreach ([DecisionTest::date(), DecisionTest::date('2099-12-31')] as $instant) {
                    for ($lecture = 0; $lecture < 2; $lecture++) {
                        $decision = (new Moteur())->decider(
                            DecisionTest::contenu(['decouverte' => true]),
                            DecisionTest::visiteur([$droit]),
                            DecisionTest::robot(),
                            $instant,
                            $reglage,
                        );
                        self::assertSame($consommes < $quota, $decision->complet);
                        self::assertSame(
                            $consommes < $quota ? 'decouverte_articles' : 'decouverte_epuisee',
                            $decision->motif->value,
                        );
                        self::assertSame($avant, $droit);
                    }
                }
            }
        }
    }

    public function testQuotaRespecteDebutVerificationEtPerimetreCommeDuree(): void
    {
        self::assertTrue(class_exists(NombreArticlesDecouverte::class));
        foreach ([false, true] as $pdf) {
            foreach (['article', 'pdf'] as $type) {
                foreach ([false, true] as $verifie) {
                    foreach (['170', '169'] as $numero) {
                        foreach ([-1, 0, 1] as $offset) {
                            $decision = (new Moteur())->decider(
                                DecisionTest::contenu(['decouverte' => true, 'type' => $type, 'numero' => $numero]),
                                DecisionTest::visiteur([DecouverteTest::droit(['compte_verifie' => $verifie])]),
                                DecisionTest::robot(),
                                DecisionTest::date()->modify(sprintf('%+d seconds', $offset)),
                                new NombreArticlesDecouverte(3, ['170'], $pdf),
                            );
                            self::assertSame(
                                $verifie && $offset >= 0 && $numero === '170' && ($type === 'article' || $pdf),
                                $decision->complet,
                            );
                        }
                    }
                }
            }
        }
    }

    public function testDecouverteNeFermeJamaisUnAchatOuAbonnementIndependant(): void
    {
        self::assertTrue(class_exists(NombreArticlesDecouverte::class));
        $reglages = [new DureeDecouverte(1, ['170'], false), new NombreArticlesDecouverte(1, ['170'], false)];
        $independants = [DroitsTest::achat(), AbonnementTest::droit(), AbonnementTest::droit(['etat' => 'grace'])];
        foreach ($reglages as $reglage) {
            $decouverte = DecouverteTest::droit(['debut' => DecisionTest::date('2026-01-01'), 'consommes' => 1]);
            foreach ($independants as $droit) {
                foreach ([[$decouverte, $droit], [$droit, $decouverte]] as $droits) {
                    $decision = (new Moteur())->decider(
                        DecisionTest::contenu(['decouverte' => true]),
                        DecisionTest::visiteur($droits),
                        DecisionTest::robot(),
                        DecisionTest::date(),
                        $reglage,
                    );
                    self::assertTrue($decision->complet);
                    self::assertNotSame('decouverte_epuisee', $decision->motif->value);
                }
            }
        }
        $avecGrace = (new Moteur())->decider(
            DecisionTest::contenu(['decouverte' => true]),
            DecisionTest::visiteur([AbonnementTest::droit(['etat' => 'grace']), DecouverteTest::droit()]),
            DecisionTest::robot(),
            DecisionTest::date(),
            new NombreArticlesDecouverte(1, ['170'], false),
        );
        self::assertTrue($avecGrace->complet);
        self::assertSame('aucun', $avecGrace->bloc->value);
        self::assertSame('decouverte_articles', $avecGrace->motif->value);
    }
}
