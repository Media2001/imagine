<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\Motif;
use Imagine\Pilotage\Acces\Reglages;
use PHPUnit\Framework\TestCase;

final class OptionsReglagesTest extends TestCase
{
    public function testHuitCombinaisonsOntUnAllerRetourSansConversionImplicite(): void
    {
        foreach (['ferme_tous', 'equipe'] as $futur) {
            foreach (['extrait', 'complet'] as $robot) {
                foreach (['ferme', 'ouvert'] as $anterieur) {
                    $options = [
                        'contenu_futur' => $futur, 'pdf_robot' => $robot,
                        'pdf_anterieur_abonnement' => $anterieur,
                    ];
                    $reglages = Reglages::depuisOptions($options);
                    self::assertSame($options, $reglages->options());
                    self::assertSame($futur === 'equipe', $reglages->contenuFuturEquipe);
                    self::assertSame($robot === 'complet', $reglages->pdfRobotComplet);
                    self::assertSame($anterieur === 'ouvert', $reglages->pdfAnterieurAbonnement);
                }
            }
        }
    }

    public function testOptionAbsenteCorrompueOuMalTypeeRevientAuDefautPrudent(): void
    {
        $defauts = ['contenu_futur' => 'ferme_tous', 'pdf_robot' => 'extrait',
            'pdf_anterieur_abonnement' => 'ferme'];
        foreach ([null, false, true, 1, 'complet', new \stdClass(), []] as $option) {
            self::assertSame($defauts, Reglages::depuisOptions($option)->options());
        }
        foreach (array_keys($defauts) as $cle) {
            foreach ([null, true, false, 1, 0, '1', 'true', ' COMplet', 'equipe ', [], new \stdClass()] as $valeur) {
                self::assertSame($defauts, Reglages::depuisOptions([$cle => $valeur])->options());
            }
        }
        self::assertSame($defauts, (new Reglages())->options());
        self::assertSame($defauts, Reglages::depuisOptions(['inconnu' => 'ouvert'])->options());
        self::assertNotContains('pdf_anterieur_a_arbitrer', array_column(Motif::cases(), 'value'));
        self::assertContains('pdf_anterieur_ferme_par_reglage', array_column(Motif::cases(), 'value'));
    }
}
