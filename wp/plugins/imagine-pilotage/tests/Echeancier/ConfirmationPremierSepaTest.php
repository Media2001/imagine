<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Echeancier;

use Imagine\Pilotage\Echeancier\Reglages;
use PHPUnit\Framework\TestCase;

final class ConfirmationPremierSepaTest extends TestCase
{
    public function testSansMargeRetientConfirmationReellePasCommande(): void
    {
        require_once __DIR__ . '/Fixture.php';
        $r = Reglages::depuisOption(['marge_jours' => '7', 'confirmation_premier_sepa' => 'sans_marge']);
        $commande = c05Date('2027-04-09 12:00:00');
        $confirmation = c05Date('2027-04-09 13:00:00');
        $payeLe = $r->premierSepaPayeLe($commande, $confirmation);
        self::assertEquals($confirmation, $payeLe);
        self::assertFalse($payeLe <= $commande);
        self::assertTrue($payeLe < c05Date('2027-04-10'));
    }

    public function testPremierSepaAttendMargeSansDeplacerNumeroNiEcheances(): void
    {
        require_once __DIR__ . '/Fixture.php';
        $annee = c05Annee('2027-04-09 12:00:00');
        $reglages = new Reglages(7);
        $payeLe = $reglages->premierSepaPayeLe($annee->debut, c05Date('2027-04-09 13:00:00'));
        self::assertEquals(c05Date('2027-04-16 12:00:00'), $payeLe);
        self::assertFalse($payeLe <= c05Date('2027-04-16 11:59:59'));
        self::assertTrue($payeLe <= c05Date('2027-04-16 12:00:00'));
        $plan = (new \Imagine\Pilotage\Echeancier\Planificateur(
            new \Imagine\Pilotage\Numeros\Moteur(c05Calendrier())
        ))->planifier($annee, $reglages->margeJours);
        self::assertSame('REG-2027-04', $plan[0]->numero->id);
        self::assertEquals($annee->debut, $plan[0]->date);
        self::assertFalse($payeLe < $plan[0]->numero->cloture, 'Pas payé avant clôture du 10 avril');
        self::assertSame('2027-07-03 00:00:00', $plan[1]->date->format('Y-m-d H:i:s'));
    }

    public function testDeuxPositionsDecodeesEtEntreesInvalidesRefusees(): void
    {
        foreach (['avec_marge', 'sans_marge'] as $position) {
            self::assertSame(
                $position,
                Reglages::depuisOption(['confirmation_premier_sepa' => $position])->confirmationPremierSepa
            );
        }
        foreach (['inconnu', '', null, true, 0, []] as $invalide) {
            try {
                Reglages::depuisOption(['confirmation_premier_sepa' => $invalide]);
                self::fail('Réglage SEPA invalide accepté');
            } catch (\InvalidArgumentException $error) {
                self::assertSame('CONFIRMATION_PREMIER_SEPA_INVALIDE', $error->getMessage());
            }
        }
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage('CONFIRMATION_PREMIER_SEPA_INVALIDE');
        new Reglages(7, 'restent_dues', 'fige_bloc', 'inconnu');
    }

    public function testMargeConfirmationPremierSepaAppliqueeParDefaut(): void
    {
        self::assertSame('avec_marge', (new Reglages())->confirmationPremierSepa);
        self::assertSame('avec_marge', Reglages::depuisOption([])->confirmationPremierSepa);
        self::assertSame(
            'avec_marge',
            Reglages::depuisOption(['marge_jours' => '7'])->confirmationPremierSepa
        );
    }
}
