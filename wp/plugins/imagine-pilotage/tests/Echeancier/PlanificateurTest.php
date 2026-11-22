<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Echeancier;

use Imagine\Pilotage\Echeancier\Planificateur;
use Imagine\Pilotage\Echeancier\Reglages;
use Imagine\Pilotage\Numeros\Activation;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Numeros\Numero;
use Imagine\Pilotage\Numeros\TypeNumero;
use DateTimeZone;
use PHPUnit\Framework\TestCase;

final class PlanificateurTest extends TestCase
{
    public static function setUpBeforeClass(): void
    {
        require_once __DIR__ . '/Fixture.php';
    }

    private static function refuse(callable $action, string $fragment): void
    {
        try {
            $action();
        } catch (\DomainException | \InvalidArgumentException $error) {
            self::assertStringContainsString($fragment, $error->getMessage());
            return;
        }
        self::fail('Un plan incompatible doit être refusé : ' . $fragment);
    }

    public function testInitialQuatreNumerosC01SansCinquieme(): void
    {
        $source = new Moteur(c05Calendrier());
        $annee = c05Annee('2027-02-20 12:00:00');
        $plan = (new Planificateur($source))->planifier($annee, 7);
        self::assertTrue(count($plan) === 4, 'Quatre positions initial compris');
        self::assertTrue(array_map(static fn ($v) => $v->numero->id, $plan) === [
            'REG-2027-04', 'REG-2027-07', 'REG-2027-10', 'REG-2028-01',
        ], 'Identifiants repris de C01');
        self::assertTrue(array_map(static fn ($v) => $v->date->format('Y-m-d H:i:s'), $plan) === [
            '2027-02-20 12:00:00', '2027-07-03 00:00:00', '2027-10-03 00:00:00', '2028-01-03 00:00:00',
        ], 'Initial remplace date commune du premier numero, pas les trois suivants');
        self::assertTrue(array_map(static fn ($v) => $v->rang, $plan) === [1, 2, 3, 4], 'Rangs');
        self::assertTrue($plan[0]->initial && !$plan[1]->initial, 'Initial marque une seule fois');
    }

    public function testReconductionCommuneEtNumerosSuivants(): void
    {
        $source = new Moteur(c05Calendrier());
        $initiale = c05Annee('2027-02-20 12:00:00');
        $debut = $initiale->finNumerique();
        $suite = $source->renouveler($initiale, $debut)->activer($debut, Activation::Paiement);
        $plan = (new Planificateur($source))->planifier($suite, 7);
        self::assertTrue(count($plan) === 4, 'Quatre communes à la reconduction');
        self::assertTrue(array_map(static fn ($v) => $v->numero->id, $plan) === [
            'REG-2028-04', 'REG-2028-07', 'REG-2028-10', 'REG-2029-01',
        ], 'Quatre suivants C01');
        foreach ($plan as $index => $v) {
            self::assertTrue(!$v->initial, 'Pas de deuxième initial');
            self::assertTrue($v->date == $source->echeances($suite, 7)[$index]->lancement, 'Date C01 exacte');
        }
    }

    public function testOptionAAccepteCinqDatesDansFenetreNumerique(): void
    {
        $source = new Moteur(c05Calendrier());
        $initiale = c05Annee('2027-04-09 12:00:00');
        $suite = $source->renouveler($initiale, $initiale->finNumerique());
        $dates = array_map(
            static fn ($v) => $v->date,
            (new Planificateur($source))->planifier($initiale, 7)
        );
        $dates[] = $source->echeances($suite, 7)[0]->lancement;
        self::assertTrue(count(array_filter(
            $dates,
            static fn ($d) => $d >= $initiale->debut && $d < $initiale->finNumerique()
        )) === 5, 'Cinq dates effectives si première reconduction commune maintenue');

        $planSuite = (new Planificateur($source))->planifier($suite, 7);
        self::assertTrue(count($planSuite) === 4, 'Bloc suivant de quatre numéros malgré anniversaire ultérieur');
        self::assertTrue($planSuite[0]->date == $dates[4], 'Date commune inchangée, aucun report anniversaire');
    }

    public function testCalendrierIncompletRefuseSansInventer(): void
    {
        $source = new Moteur(new Calendrier(array_slice(c05Calendrier()->numeros, 0, 2)));
        $annee = c05Annee('2026-01-01');
        self::refuse(
            static fn () => (new Planificateur($source))->planifier($annee, 7),
            'CALENDRIER_INCOMPLET'
        );
    }

    public function testCloturesIdentiquesRefuseesSansDeplacer(): void
    {
        $n = c05Calendrier()->numeros;
        $n[2] = new Numero($n[2]->id, $n[2]->type, $n[2]->sortie, $n[1]->cloture);
        $source = new Moteur(new Calendrier($n));
        $annee = c05Annee('2026-01-01');
        self::refuse(
            static fn () => (new Planificateur($source))->planifier($annee, 7),
            'DATES_NON_CROISSANTES'
        );
    }

    public function testApiSansFinEngagementEtProjectionAnneeNonActivee(): void
    {
        $methode = new \ReflectionMethod(Planificateur::class, 'planifier');
        self::assertSame(
            ['annee', 'margeJours'],
            array_map(static fn (\ReflectionParameter $p): string => $p->getName(), $methode->getParameters())
        );
        $annee = new \Imagine\Pilotage\Numeros\Annee(c05Date('2027-02-20 12:00:00'));
        self::assertNull($annee->finNumerique());
        $plan = (new Planificateur(new Moteur(c05Calendrier())))->planifier($annee, 7);
        self::assertCount(4, $plan);
        self::assertEquals($annee->debut, $plan[0]->date);
    }

    public function testMargeObligatoireEtParametrable(): void
    {
        $annee = c05Annee('2027-02-20 12:00:00');
        $planner = new Planificateur(new Moteur(c05Calendrier()));
        foreach ([0, -1] as $marge) {
            self::refuse(static fn () => $planner->planifier($annee, $marge), 'marge');
        }
        foreach ([1, 3, 7] as $marge) {
            $plan = $planner->planifier($annee, $marge);
            self::assertTrue(
                $plan[1]->date->format('Y-m-d') === sprintf('2027-07-%02d', 10 - $marge),
                'Marge injectée'
            );
            self::assertTrue($plan[0]->date == $annee->debut, 'Initial indépendant de la marge');
        }
    }

    public function testReglageMargeSansDefautRefusePlanification(): void
    {
        $reglages = new Reglages();
        self::assertTrue($reglages->margeJours === null, 'Aucun défaut de marge');
        $a = c05Annee('2027-02-20');
        $planner = new Planificateur(new Moteur(c05Calendrier()));
        self::refuse(static fn () => $planner->planifier($a, $reglages->margeJours), 'MARGE_OBLIGATOIRE');
        self::refuse(static fn () => $planner->planifier($a), 'MARGE_OBLIGATOIRE');
        foreach ([0, -1] as $invalid) {
            self::refuse(static fn () => new Reglages($invalid), 'marge');
        }
        foreach ([1, 3, 7, 30] as $marge) {
            $r = new Reglages($marge);
            $p = $planner->planifier($a, $r->margeJours);
            self::assertTrue(
                $p[1]->date == c05Date('2027-07-10')->modify('-' . $marge . ' days'),
                'Jours civils configurés'
            );
        }
    }

    public function testReglageRejetResteDuDefautEtAbandonExplicite(): void
    {
        $defaut = new Reglages(7);
        self::assertTrue($defaut->apresRejet === 'restent_dues', 'Défaut prudent : dette maintenue');
        self::assertTrue(
            $defaut->montantsRestants(1000, 1000, [1], true) === [2 => 1000, 3 => 1000, 4 => 1000],
            'Rejet ne remet aucune dette'
        );
        $autre = new Reglages(7, 'annuler_restantes');
        self::assertTrue($autre->montantsRestants(1000, 1000, [1], true) === [], 'Alternative explicite après rejet');
        self::assertTrue(
            $autre->montantsRestants(1000, 1000, [1], false) === [2 => 1000, 3 => 1000, 4 => 1000],
            'Sans rejet aucune remise'
        );
        self::assertTrue(
            $defaut->montantsRestants(1000, 1000, [1, 2, 3, 4], true) === [],
            'Aucun rang payé redevient dû'
        );
        self::refuse(static fn () => new Reglages(7, 'inconnu'), 'REJET_INVALIDE');
        self::refuse(static fn () => $defaut->montantsRestants(-1, 1000, [], true), 'MONTANT_INVALIDE');
        self::refuse(static fn () => $defaut->montantsRestants(1000, 1000, [5], true), 'RANG_INVALIDE');
    }

    public function testReglageTarifFigeBlocDefautEtCourantSeulementImpayes(): void
    {
        $defaut = new Reglages(7);
        self::assertTrue($defaut->tarif === 'fige_bloc', 'Tarif figé pour les quatre échéances');
        foreach ([800, 1200] as $courant) {
            self::assertTrue(
                $defaut->montantsRestants(1000, $courant, [1], false) === [2 => 1000, 3 => 1000, 4 => 1000],
                'Hausse/baisse sans effet bloc'
            );
            $autre = new Reglages(7, 'restent_dues', 'courant_impayes');
            self::assertTrue(
                $autre->montantsRestants(1000, $courant, [1, 2], false) === [3 => $courant, 4 => $courant],
                'Seuls rangs impayés au tarif courant'
            );
            self::assertTrue(
                $autre->montantsRestants(1000, $courant, [1, 2], true) === [3 => $courant, 4 => $courant],
                'Rejet conserve créances au tarif choisi'
            );
            $annulation = new Reglages(7, 'annuler_restantes', 'courant_impayes');
            self::assertTrue(
                $annulation->montantsRestants(1000, $courant, [1], true) === [],
                'Annulation explicite prioritaire'
            );
        }
        self::assertTrue(
            $defaut->montantsRestants(1200, 1200, [], false) === [1 => 1200, 2 => 1200, 3 => 1200, 4 => 1200],
            'Bloc reconduit capture nouveau tarif'
        );
        self::refuse(static fn () => new Reglages(7, 'restent_dues', 'inconnu'), 'TARIF_INVALIDE');
        self::refuse(static fn () => $defaut->montantsRestants(1000, -1, [], false), 'MONTANT_INVALIDE');
    }

    public function testReglagesOptionDecodeStrictEtMatriceComplete(): void
    {
        self::assertTrue(Reglages::depuisOption([])->margeJours === null, 'Option absente ne crée pas une marge');
        self::assertTrue(
            Reglages::depuisOption(['marge_jours' => ''])->margeJours === null,
            'Champ vide désactive planification'
        );
        foreach ([1, 3, 7, 30] as $marge) {
            foreach (['restent_dues', 'annuler_restantes'] as $rejet) {
                foreach (['fige_bloc', 'courant_impayes'] as $tarif) {
                    $r = Reglages::depuisOption([
                        'marge_jours' => (string) $marge, 'apres_rejet' => $rejet, 'tarif' => $tarif,
                    ]);
                    self::assertTrue(
                        $r->margeJours === $marge && $r->apresRejet === $rejet && $r->tarif === $tarif,
                        'Toutes combinaisons réglages'
                    );
                }
            }
        }
        foreach (['0', '-1', '7.5', '7 jours', true, [], '99999999999999999999999999999'] as $invalid) {
            self::refuse(static fn () => Reglages::depuisOption(['marge_jours' => $invalid]), 'MARGE_INVALIDE');
        }
        self::refuse(static fn () => Reglages::depuisOption('corrompu'), 'REGLAGES_INVALIDES');
        self::refuse(static fn () => Reglages::depuisOption(['apres_rejet' => []]), 'REJET_INVALIDE');
        self::refuse(static fn () => Reglages::depuisOption(['tarif' => false]), 'TARIF_INVALIDE');
    }

    public function testJourClotureEtLendemainPassentAuNumeroSuivant(): void
    {
        $source = new Moteur(c05Calendrier());
        foreach (['2027-04-10 00:00:00', '2027-04-10 12:00:00', '2027-04-11 12:00:00'] as $date) {
            $a = c05Annee($date);
            $plan = (new Planificateur($source))->planifier($a, 7);
            self::assertTrue($plan[0]->numero->id === 'REG-2027-07', 'Clôture incluse C01');
            $b = $source->renouveler($a, $a->finNumerique());
            $suite = (new Planificateur($source))->planifier($b, 7);
            self::assertTrue($suite[0]->numero->id === 'REG-2028-07', 'Suivant sans doublon');
        }
    }

    public function testFuseauDstEt29FevrierSontCeuxDeC01(): void
    {
        $source = new Moteur(c05Calendrier());
        $a = c05Annee('2028-02-29 10:30:00');
        self::assertTrue($a->finNumerique()->format('Y-m-d H:i:s') === '2029-02-28 10:30:00', 'Anniversaire C01');
        $plan = (new Planificateur($source))->planifier($a, 7);
        self::assertTrue($plan[1]->date->format('P') === '+02:00', 'Été C01');
        self::assertTrue($plan[3]->date->format('P') === '+01:00', 'Hiver C01');
        $utc = $a->debut->setTimezone(new DateTimeZone('UTC'));
        $other = c05Annee($utc->format(DATE_ATOM));
        self::assertTrue(
            (new Planificateur($source))->planifier($other, 7)[0]->date == $plan[0]->date,
            'Instant absolu'
        );
    }

    public function testContreExempleA00CinqDatesNaivesQuatrePositions(): void
    {
        $source = new Moteur(c05Calendrier());
        $a = c05Annee('2027-02-20 12:00:00');
        $naives = [$a->debut];
        foreach ($source->calendrier->numeros as $n) {
            if ($n->type === TypeNumero::Regulier && $n->cloture > $a->debut && $n->cloture < $a->finNumerique()) {
                $naives[] = $n->cloture;
            }
        }
        self::assertTrue(count($naives) === 5, 'Cinq dates si on ajoute toutes les clôtures');
        self::assertTrue(
            count((new Planificateur($source))->planifier($a, 7)) === 4,
            'Le premier numéro est payé à la commande'
        );
    }

    public function testReconductionInconnueSiPrecedenteIncomplete(): void
    {
        $source = new Moteur(new Calendrier(array_slice(c05Calendrier()->numeros, 0, 2)));
        $a = c05Annee('2026-01-01');
        $b = $source->renouveler($a, $a->finNumerique());
        self::refuse(
            static fn () => (new Planificateur($source))->planifier($b, 7),
            'CALENDRIER_INCOMPLET'
        );
    }

    public function testCloturesEgalesJonctionRang4Rang1RefuseesExplicitement(): void
    {
        $moteur = new Moteur(c05CalendrierJonctionEgale());
        $initiale = c05Annee('2027-02-20 12:00:00');
        $planner = new Planificateur($moteur);
        $initial = $planner->planifier($initiale, 7);
        $suite = $moteur->renouveler($initiale, $initiale->finNumerique());
        self::assertSame('2028-01-03 00:00:00', $initial[3]->date->format('Y-m-d H:i:s'));
        self::assertEquals($initial[3]->date, $moteur->echeances($suite, 7)[0]->lancement);
        self::refuse(
            static fn () => $planner->planifier($suite, 7),
            'DATES_NON_CROISSANTES'
        );
    }

    public function test09AvrilGardeCommunesEtCinqDatesAvecChronologieInterBlocs(): void
    {
        $moteur = new Moteur(c05Calendrier());
        $a = c05Annee('2027-04-09 12:00:00');
        $b = $moteur->renouveler($a, $a->finNumerique());
        $planner = new Planificateur($moteur);
        $initial = $planner->planifier($a, 7);
        $suite = $planner->planifier($b, 7);
        self::assertTrue($initial[3]->date < $suite[0]->date);
        self::assertSame('2028-04-03', $suite[0]->date->format('Y-m-d'));
        self::assertTrue($suite[0]->date < $a->finNumerique());
        self::assertCount(4, $initial);
        self::assertCount(4, $suite);
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('jours2027')]
    public function testAnneeComplete(string $date): void
    {
        $source = new Moteur(c05Calendrier());
        $a = c05Annee($date);
        $planner = new Planificateur($source);
        $p = $planner->planifier($a, 7);
        self::assertTrue(count($p) === 4, 'Quatre initial compris');
        self::assertTrue(
            array_map(static fn ($v) => $v->numero->id, $p)
                === array_map(static fn ($n) => $n->id, $source->numeros($a)),
            'C01 seul sélectionne'
        );
        $b = $source->renouveler($a, $a->finNumerique())->activer($a->finNumerique(), Activation::Paiement);
        $premiereCommune = $source->echeances($b, 7)[0]->lancement;
        $suite = $planner->planifier($b, 7);
        self::assertTrue(count($suite) === 4, 'Reconduction quatre par bloc');
        self::assertTrue($suite[0]->date == $premiereCommune, 'Commune sans exception anniversaire');
        self::assertTrue($suite[0]->date > $p[3]->date, 'Chronologie inter-blocs');
        $dates = array_map(static fn ($v) => $v->date, [...$p, ...$suite]);
        $dansFenetre = count(array_filter($dates, static fn ($d) => $d >= $a->debut && $d < $a->finNumerique()));
        self::assertTrue($dansFenetre === ($premiereCommune < $b->debut ? 5 : 4), 'Comptage fenêtre distinct du bloc');
    }

    public function testVingtHuitFenetresACinqDatesSur365Commandes(): void
    {
        $moteur = new Moteur(c05Calendrier());
        $planner = new Planificateur($moteur);
        $total = 0;
        foreach (self::jours2027() as [$date]) {
            $a = c05Annee($date);
            $b = $moteur->renouveler($a, $a->finNumerique());
            $positions = [...$planner->planifier($a, 7), ...$planner->planifier($b, 7)];
            $dates = array_map(static fn ($v) => $v->date, $positions);
            $nombre = count(array_filter($dates, static fn ($d) => $d >= $a->debut && $d < $a->finNumerique()));
            $total += (int) ($nombre === 5);
        }
        self::assertSame(28, $total);
    }

    public static function jours2027(): iterable
    {
        $zone = new DateTimeZone('Europe/Brussels');
        $fin = new \DateTimeImmutable('2028-01-01', $zone);
        $debut = new \DateTimeImmutable('2027-01-01 12:00:00', $zone);
        for ($jour = $debut; $jour < $fin; $jour = $jour->modify('+1 day')) {
            yield $jour->format('Y-m-d') => [$jour->format('Y-m-d H:i:s')];
        }
    }
}
