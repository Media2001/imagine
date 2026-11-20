<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Numeros;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\Activation;
use Imagine\Pilotage\Numeros\Annee;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Numeros\Numero;
use Imagine\Pilotage\Numeros\TypeNumero;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class InvariantsTest extends TestCase
{
    private function date(string $date): DateTimeImmutable
    {
        return new DateTimeImmutable($date, new DateTimeZone('Europe/Brussels'));
    }

    private function numero(string $id = '171', string $sortie = '2027-01-05', string $cloture = '2026-12-20'): Numero
    {
        return new Numero($id, TypeNumero::Regulier, $this->date($sortie), $this->date($cloture));
    }

    public function testDeplacerUnFuturNePeutEvincerUnNumeroDejaCloture(): void
    {
        $calendrier = new Calendrier([
            $this->numero('171', '2027-01-05', '2026-12-20'),
            $this->numero('172', '2027-04-05', '2027-03-20'),
            $this->numero('173', '2027-07-05', '2027-06-20'),
            $this->numero('174', '2027-10-05', '2027-09-20'),
            $this->numero('175', '2028-01-05', '2027-12-20'),
        ]);
        $this->expectException(\LogicException::class);
        $calendrier->modifier($this->numero('175', '2027-10-01', '2027-09-25'), $this->date('2027-09-21'));
    }

    public static function transitionsInvalides(): array
    {
        return [
            'pas de paiement' => ['sans-paiement'],
            'deja actif' => ['reactivation-active'],
            'double suspension' => ['double-suspension'],
            'retour chronologique' => ['retour'],
            'activation trop tot' => ['activation-avant'],
            'deux activations' => ['double-activation'],
            'historique injecte invalide' => ['injection'],
            'renouvellement trop tot' => ['renouvellement'],
        ];
    }

    #[DataProvider('transitionsInvalides')]
    public function testTransitionsInvalidesRefusees(string $cas): void
    {
        $annee = new Annee($this->date('2026-10-08'));
        $this->expectException(\LogicException::class);
        if ($cas === 'sans-paiement') {
            $annee->suspendre($this->date('2026-10-09'));
        } elseif ($cas === 'activation-avant') {
            $annee->activer($this->date('2026-10-07'), Activation::Paiement);
        } elseif ($cas === 'injection') {
            new Annee($this->date('2026-10-08'), null, null, null, [$this->date('2026-10-09')]);
        } elseif ($cas === 'renouvellement') {
            (new Moteur(new Calendrier([])))->renouveler($annee, $annee->debut);
        } else {
            $active = $annee->activer($annee->debut, Activation::Paiement);
            if ($cas === 'double-activation') {
                $active->activer($this->date('2026-10-09'), Activation::Mandat);
            } elseif ($cas === 'reactivation-active') {
                $active->reactiver($this->date('2026-10-09'));
            } else {
                $suspendue = $active->suspendre($this->date('2026-10-10'));
                if ($cas === 'double-suspension') {
                    $suspendue->suspendre($this->date('2026-10-11'));
                } else {
                    $suspendue->reactiver($this->date('2026-10-09'));
                }
            }
        }
    }

    public function testMargeDeZeroRefusee(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        (new Moteur(new Calendrier([])))->echeances(new Annee($this->date('2026-10-08')), 0);
    }

    public function testMargeNegativeRefusee(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        (new Moteur(new Calendrier([])))->echeances(new Annee($this->date('2026-10-08')), -2);
    }

    public function testNumeroVideRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->numero('');
    }

    public function testSortieAvantClotureRefusee(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->numero('171', '2026-12-01', '2026-12-20');
    }

    public function testIdentifiantsDoublesRefuses(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Calendrier([$this->numero(), $this->numero()]);
    }

    public function testObjetInvalideRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Calendrier(['171']);
    }

    public function testAnniversaireDu29FevrierResteAArbitrer(): void
    {
        $annee = (new Annee($this->date('2028-02-29')))->activer($this->date('2028-02-29'), Activation::Paiement);
        $this->expectException(\LogicException::class);
        $annee->finNumerique();
    }

    public function testDatesNormaliseesEtObjetsImmuables(): void
    {
        $utc = new DateTimeImmutable('2026-12-19T23:00:00Z');
        $numero = new Numero('171', TypeNumero::Regulier, $this->date('2027-01-05'), $utc);
        self::assertSame('2026-12-20 00:00:00 Europe/Brussels', $numero->cloture->format('Y-m-d H:i:s e'));
        self::assertSame('2026-12-19T23:00:00+00:00', $utc->format('c'));
        $classes = [Numero::class, Calendrier::class, Annee::class, Moteur::class];
        $classes[] = \Imagine\Pilotage\Numeros\Echeance::class;
        foreach ($classes as $class) {
            self::assertTrue((new \ReflectionClass($class))->isReadOnly());
        }
    }

    public function testEcheanceNormaliseAussiLaDateInjectee(): void
    {
        $echeance = new \Imagine\Pilotage\Numeros\Echeance(
            $this->numero(),
            new DateTimeImmutable('2026-12-12T23:00:00Z')
        );
        self::assertSame('2026-12-13 00:00:00 Europe/Brussels', $echeance->lancement->format('Y-m-d H:i:s e'));
    }

    public function testMargeTraverseHeureDEteEnJoursEtNonEnSecondes(): void
    {
        $moteur = new Moteur(new Calendrier([$this->numero('172', '2027-04-05', '2027-03-30')]));
        $date = $moteur->echeances(new Annee($this->date('2027-03-01')), 7)[0]->lancement;
        self::assertSame('2027-03-23 00:00:00 +01:00', $date->format('Y-m-d H:i:s P'));
    }

    public function testClotureRetroactiveRefusee(): void
    {
        $this->expectException(\LogicException::class);
        (new Calendrier([$this->numero()]))->modifier(
            $this->numero('171', '2027-01-05', '2026-11-01'),
            $this->date('2026-11-02')
        );
    }

    public function testNumeroInconnuNePeutEtreModifie(): void
    {
        $this->expectException(\OutOfBoundsException::class);
        (new Calendrier([]))->modifier($this->numero(), $this->date('2026-11-02'));
    }

    public function testTypeNePeutChanger(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        (new Calendrier([$this->numero()]))->modifier(
            new Numero('171', TypeNumero::HorsSerie, $this->date('2027-01-05'), $this->date('2026-12-20')),
            $this->date('2026-11-02')
        );
    }
}
