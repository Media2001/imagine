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
