<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\Moteur;
use Imagine\Pilotage\Acces\Reglages;
use Imagine\Pilotage\Robots\Decision as DecisionRobot;
use Imagine\Pilotage\Robots\Motif as MotifRobot;
use PHPUnit\Framework\TestCase;

final class ReglagesTest extends TestCase
{
    public function testPdfRobotDeuxPositionsEtFauxRobotNeRecoitPasDeDroit(): void
    {
        foreach ([false, true] as $complet) {
            foreach ([true, false] as $verifie) {
                $decision = (new Moteur())->decider(
                    DecisionTest::contenu(['type' => 'pdf']),
                    DecisionTest::visiteur([], false),
                    $verifie ? new DecisionRobot(MotifRobot::VerifieDns, 'google') : DecisionTest::robot(),
                    DecisionTest::date(),
                    null,
                    new Reglages(pdfRobotComplet: $complet),
                );
                self::assertSame($complet && $verifie, $decision->complet);
                self::assertSame(
                    !$verifie ? 'anonyme' : ($complet ? 'robot_verifie' : 'pdf_robot_extrait_par_reglage'),
                    $decision->motif->value,
                );
            }
        }
    }

    public function testSortieFutureDeuxPositionsNeBeneficientQuaEquipeValide(): void
    {
        $profils = [
            [DecisionTest::visiteur([], false), DecisionTest::robot(), false],
            [DecisionTest::visiteur([AbonnementTest::droit()]), DecisionTest::robot(), false],
            [DecisionTest::visiteur([DroitsTest::achat()]), DecisionTest::robot(), false],
            [DecisionTest::visiteur(), new DecisionRobot(MotifRobot::VerifieDns, 'google'), false],
            [DecisionTest::visiteur([['type' => 'equipe', 'role' => 'redaction']]), DecisionTest::robot(), true],
            [DecisionTest::visiteur([['type' => 'equipe', 'role' => 'administration']]), DecisionTest::robot(), true],
        ];
        foreach ([false, true] as $ouvrirEquipe) {
            foreach ($profils as [$visiteur, $robot, $equipe]) {
                foreach (['article', 'pdf'] as $type) {
                    foreach ([false, true] as $reserve) {
                        $decision = (new Moteur())->decider(
                            DecisionTest::contenu([
                                'reserve' => $reserve, 'type' => $type,
                                'sortie' => DecisionTest::date('2026-11-21 12:00:01'),
                            ]),
                            $visiteur,
                            $robot,
                            DecisionTest::date(),
                            null,
                            $ouvrirEquipe ? new Reglages(contenuFuturEquipe: true) : null,
                        );
                        $attendu = $ouvrirEquipe && $equipe;
                        self::assertSame($attendu, $decision->complet);
                        self::assertSame(
                            $attendu ? 'contenu_futur_equipe_par_reglage' : 'contenu_futur_ferme_par_reglage',
                            $decision->motif->value,
                        );
                        self::assertSame($attendu ? 'aucun' : 'abonnement', $decision->bloc->value);
                    }
                }
            }
        }
    }

    public function testPdfAnterieurDeuxPositionsRespectentDatesEtEtatsDesTroisAbonnements(): void
    {
        foreach ([false, true] as $ouvrirPdf) {
            foreach (['abonnement', 'offert', 'groupe'] as $type) {
                foreach (['actif', 'grace', 'suspendu', 'expire', 'virement_non_valide'] as $etat) {
                    foreach (
                        ['2026-10-31 23:59:59', '2026-11-01 00:00:00', '2026-11-30 23:59:59',
                        '2026-12-01 00:00:00'] as $date
                    ) {
                        $dansDates = $date >= '2026-11-01 00:00:00' && $date < '2026-12-01 00:00:00';
                        $actif = in_array($etat, ['actif', 'grace'], true);
                        $decision = (new Moteur())->decider(
                            DecisionTest::contenu(['type' => 'pdf']),
                            DecisionTest::visiteur([AbonnementTest::droit([
                                'type' => $type, 'etat' => $etat, 'debut' => DecisionTest::date('2026-11-01'),
                            ])]),
                            DecisionTest::robot(),
                            DecisionTest::date($date),
                            null,
                            $ouvrirPdf ? new Reglages(pdfAnterieurAbonnement: true) : null,
                        );
                        self::assertSame($ouvrirPdf && $actif && $dansDates, $decision->complet);
                        $motif = !$actif ? $etat : (!$dansDates
                            ? ($date < '2026-11-01 00:00:00' ? 'abonnement_pas_commence' : 'expire')
                            : (!$ouvrirPdf ? 'pdf_anterieur_ferme_par_reglage'
                                : ($etat === 'grace' ? 'delai_grace' : $type . '_actif')));
                        self::assertSame($motif, $decision->motif->value);
                        if ($decision->complet) {
                            self::assertSame($etat === 'grace' ? 'regularisation' : 'aucun', $decision->bloc->value);
                        }
                    }
                }
            }
        }
    }

    public function testRobotFermeNeRetirePasUnAchatOuUnDroitEquipeOuAbonnementValide(): void
    {
        $droits = [DroitsTest::achat(), ['type' => 'equipe', 'role' => 'redaction'], AbonnementTest::droit()];
        foreach ($droits as $droit) {
            $decision = (new Moteur())->decider(
                DecisionTest::contenu(['type' => 'pdf']),
                DecisionTest::visiteur([$droit]),
                new DecisionRobot(MotifRobot::VerifieDns, 'google'),
                DecisionTest::date(),
            );
            self::assertTrue($decision->complet);
            self::assertSame(match ($droit['type']) {
                'achat' => 'numero_achete', 'equipe' => 'equipe', default => 'abonnement_actif',
            }, $decision->motif->value);
        }
    }

    public function testPdfRobotEstExtraitParDefautSansFermerLesArticles(): void
    {
        foreach (['google', 'bing'] as $identite) {
            foreach ([MotifRobot::VerifieDns, MotifRobot::VerifiePlage] as $motif) {
                $robot = new DecisionRobot($motif, $identite);
                $pdf = (new Moteur())->decider(
                    DecisionTest::contenu(['type' => 'pdf']),
                    DecisionTest::visiteur([], false),
                    $robot,
                    DecisionTest::date(),
                );
                self::assertFalse($pdf->complet);
                self::assertSame('pdf_robot_extrait_par_reglage', $pdf->motif->value);
                self::assertSame('abonnement', $pdf->bloc->value);
                $article = (new Moteur())->decider(
                    DecisionTest::contenu(),
                    DecisionTest::visiteur([], false),
                    $robot,
                    DecisionTest::date(),
                );
                self::assertTrue($article->complet);
                self::assertSame('robot_verifie', $article->motif->value);
            }
        }
    }
}
